"""Bounded SQL sessions, catalog evidence and acknowledged workload ledger."""
from __future__ import annotations
import threading
import time
import psycopg


class Context:
    def __init__(self, cluster, evidence, observe=True):
        self.cluster, self.evidence = cluster, evidence
        self.observe = observe
        self.admin = cluster.connect('observer')
        self.checks, self.details = [], {}
        self.expected = {i:'v-'+str(i) for i in range(1,101)}
        self.ledger = []
        self._mutex=threading.Lock()
        self.threads=[]
        self.samples=0

    def sql(self, c, query, params=None, required=True):
        start=time.monotonic()
        try:
            cur=c.execute(query,params)
            rows=cur.fetchall() if cur.description else []
            outcome=dict(ok=True,rows=rows,sqlstate=None)
        except psycopg.Error as e:
            outcome=dict(ok=False,rows=[],sqlstate=e.sqlstate,error=str(e))
        outcome['event']=self.evidence.event('sql',pid=c.info.backend_pid,query=query,params=params,
            elapsed_query_s=time.monotonic()-start,transaction_status=c.info.transaction_status.name,**outcome)
        if required and not outcome['ok']:
            raise RuntimeError('Unexpected SQL failure '+str(outcome['sqlstate'])+': '+query)
        return outcome

    def check(self, name, ok, **evidence):
        item=dict(name=name,ok=ok,**evidence)
        self.checks.append(item)
        self.evidence.event('invariant',**item)

    def snapshot(self, phase):
        a=self.sql(self.admin,"SELECT pid,application_name,state,wait_event_type,wait_event,xact_start,backend_xid,backend_xmin,pg_blocking_pids(pid),query FROM pg_stat_activity WHERE datname=current_database() ORDER BY pid")
        l=self.sql(self.admin,"SELECT pid,locktype,mode,granted,relation,virtualxid,transactionid FROM pg_locks WHERE database=(SELECT oid FROM pg_database WHERE datname=current_database()) OR pid IN (SELECT pid FROM pg_stat_activity WHERE datname=current_database()) ORDER BY pid,locktype,mode")
        self.samples+=1
        return self.evidence.event('observation',phase=phase,activity_event=a['event'],locks_event=l['event'])

    def wait(self, predicate, name, timeout=8):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if predicate():
                self.evidence.event('barrier',name=name,status='REACHED')
                return
            time.sleep(.02)
        self.evidence.event('barrier',name=name,status='TIMEOUT')
        raise TimeoutError('Observation barrier not reached: '+name)

    def fork(self, fn):
        errors=[]
        def worker():
            try: fn()
            except BaseException as e: errors.append(e)
        t=threading.Thread(target=worker,daemon=True)
        self.threads.append((t,errors)); t.start()
        return t

    def join(self, t):
        t.join(12)
        if t.is_alive():
            raise TimeoutError('Worker failed to finish under SQL timeout')
        for thread,errors in self.threads:
            if thread is t and errors:
                raise RuntimeError('Worker failed: '+str(errors[0])) from errors[0]

    def setup(self):
        self.sql(self.admin,'CREATE TABLE business(id integer PRIMARY KEY,value text NOT NULL)')
        with self.admin.cursor() as cur:
            cur.executemany('INSERT INTO business VALUES(%s,%s)',list(self.expected.items()))
        self.evidence.event('seed',rows=list(self.expected.items()),source='synthetic deterministic, not production')

    def metadata(self, phase):
        queries={
            'columns':"SELECT table_schema,table_name,column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position",
            'indexes':"SELECT c.relname,i.indisvalid,i.indisready,i.indisunique,pg_get_indexdef(i.indexrelid) FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY c.relname",
            'constraints':"SELECT c.conname,c.contype,c.convalidated,pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname='public' ORDER BY c.conname",
            'acl':"SELECT c.relname,c.relowner::regrole::text,c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY c.relname",
        }
        data={k:self.sql(self.admin,q)['rows'] for k,q in queries.items()}
        self.evidence.event('metadata',phase=phase,data=data)
        return data

    def workload(self):
        """60 deterministic, disjoint-key single-statement committed mutations."""
        def writer(w):
            with self.cluster.connect('writer'+str(w)) as c:
                for i in range(1,11):
                    key=1000+w*100+i; val='insert-'+str(key)
                    ops=[('insert',key,val,'INSERT INTO business VALUES(%s,%s)',(key,val)),
                         ('update',w*10+i,'updated-'+str(w*10+i),'UPDATE business SET value=%s WHERE id=%s',('updated-'+str(w*10+i),w*10+i)),
                         ('delete',50+w*10+i,None,'DELETE FROM business WHERE id=%s',(50+w*10+i,))]
                    for op,k,v,sql,params in ops:
                        outcome=self.sql(c,sql,params,required=False)
                        with self._mutex:
                            if outcome['ok']:
                                # Expected values derive from intended operations, not a SELECT of actual DB.
                                if op=='delete': self.expected.pop(k)
                                else: self.expected[k]=v
                                self.ledger.append(dict(op=op,id=k,value=v,event=outcome['event']))
                            else:
                                self.check('acknowledged workload has no SQL error',False,event=outcome['event'])
                    time.sleep(.01)
        threads=[self.fork(lambda w=w:writer(w)) for w in range(2)]
        self.wait(lambda:len(self.ledger)>=6,'both writers started')
        return threads

    def final_data(self):
        from .oracles import compare_rows
        validator=self.cluster.connect('committed_business_oracle')
        rows=self.sql(validator,'SELECT id,value FROM business ORDER BY id')['rows']
        result=compare_rows(self.expected,rows)
        self.check('acknowledged business ledger',result.pop('ok'),**result)
        self.evidence.write_json('business-ledger.json',dict(initial_rows=100,acknowledged=self.ledger,expected=sorted(self.expected.items()),actual=rows))

    def close_workers(self):
        # Must finish or fail before cluster cleanup and evidence seal.
        for t,_ in self.threads:
            if t.is_alive():
                self.join(t)
