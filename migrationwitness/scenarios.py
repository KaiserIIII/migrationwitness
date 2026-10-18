"""Predeclared native scenarios. Constructed failures are never called upstream bugs."""
CONTROLS={
    'lock_timeout':'PASS','concurrent_dml':'PASS','old_new_clients_safe':'PASS',
    'old_new_clients_break':'FAIL','index_cancel':'FAIL','index_recover':'PASS',
    'backfill_bad':'FAIL','backfill_safe':'PASS','constraints_safe':'PASS',
    'privileges_bad':'FAIL','privileges_safe':'PASS','partial_recovery':'PASS',
}


def lock_timeout(ctx):
    with ctx.cluster.connect('blocker') as blocker,ctx.cluster.connect('ddl') as ddl:
        ctx.sql(blocker,'BEGIN'); ctx.sql(blocker,'SELECT * FROM business LIMIT 1')
        ctx.sql(ddl,"SET lock_timeout='1200ms'")
        result={}
        t=ctx.fork(lambda:result.update(ctx.sql(ddl,'ALTER TABLE business ADD COLUMN blocked int',required=False)))
        ctx.wait(lambda:bool(ctx.admin.execute('SELECT 1 FROM pg_locks WHERE pid=%s AND NOT granted',(ddl.info.backend_pid,)).fetchone()),'DDL ungranted lock')
        blockers=ctx.admin.execute('SELECT pg_blocking_pids(%s)',(ddl.info.backend_pid,)).fetchone()[0]
        ctx.snapshot('DDL blocked by long transaction'); ctx.join(t)
        ctx.sql(blocker,'ROLLBACK')
        columns=ctx.sql(ctx.admin,"SELECT attname FROM pg_attribute WHERE attrelid='business'::regclass AND attnum>0 AND NOT attisdropped")['rows']
        observed=blocker.info.backend_pid in blockers
        ctx.details.update(sqlstate=result['sqlstate'],blocker_observed=observed)
        ctx.check('lock timeout, observed blocker, no partial column',result['sqlstate']=='55P03' and observed and ('blocked',) not in columns,event=result['event'])


def concurrent_dml(ctx):
    threads=ctx.workload()
    if ctx.observe: ctx.snapshot('writes active before additive DDL')
    ctx.sql(ctx.admin,'ALTER TABLE business ADD COLUMN note text')
    if ctx.observe: ctx.snapshot('writes active after additive DDL')
    for t in threads: ctx.join(t)
    ctx.details.update(acknowledged_operations=len(ctx.ledger),observer_samples=ctx.samples)
    ctx.check('all scheduled mutations acknowledged',len(ctx.ledger)==60)


def old_new(ctx, broken):
    import threading
    old=ctx.cluster.connect('old_client'); new=ctx.cluster.connect('new_client')
    ready=threading.Event(); continue_after=threading.Event(); outcomes=[]
    def reader():
        outcomes.append(ctx.sql(old,'SELECT id,value FROM business ORDER BY id LIMIT 1',required=False))
        ready.set()
        if not continue_after.wait(8): raise TimeoutError('client release missing')
        outcomes.append(ctx.sql(old,'SELECT id,value FROM business ORDER BY id LIMIT 1',required=False))
    t=ctx.fork(reader)
    ctx.wait(ready.is_set,'old client before migration')
    writers=ctx.workload()
    if broken: ctx.sql(ctx.admin,'ALTER TABLE business RENAME COLUMN value TO renamed_value')
    else: ctx.sql(ctx.admin,'ALTER TABLE business ADD COLUMN new_value text')
    continue_after.set()
    query='SELECT id,renamed_value FROM business LIMIT 1' if broken else 'SELECT id,value,new_value FROM business LIMIT 1'
    result=ctx.sql(new,query,required=False)
    ctx.join(t)
    for w in writers: ctx.join(w)
    ctx.check('old client projection remains usable',all(x['ok'] for x in outcomes),events=[x['event'] for x in outcomes])
    ctx.check('new client projection usable',result['ok'],event=result['event'])
    ctx.details['old_client_sqlstates']=[o['sqlstate'] for o in outcomes]
    # Restore source spelling solely for final ledger inspection, after evidence of the break.
    if broken: ctx.sql(ctx.admin,'ALTER TABLE business RENAME COLUMN renamed_value TO value')


def index(ctx, recover):
    blocker=ctx.cluster.connect('writer_blocker'); migrator=ctx.cluster.connect('index_builder')
    ctx.sql(blocker,'BEGIN');ctx.sql(blocker,'UPDATE business SET value=value WHERE id=1')
    result={}
    t=ctx.fork(lambda:result.update(ctx.sql(migrator,'CREATE INDEX CONCURRENTLY business_value_idx ON business(value)',required=False)))
    ctx.wait(lambda:bool(ctx.admin.execute("SELECT 1 FROM pg_stat_activity WHERE pid=%s AND wait_event_type='Lock'",(migrator.info.backend_pid,)).fetchone()),'concurrent index blocked')
    ctx.snapshot('concurrent index waiting')
    migrator.cancel_safe();ctx.evidence.event('fault',action='cancel_safe',pid=migrator.info.backend_pid)
    ctx.join(t);ctx.sql(blocker,'ROLLBACK')
    rows=ctx.sql(ctx.admin,"SELECT c.relname,i.indisvalid,i.indisready FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid WHERE c.relname='business_value_idx'")['rows']
    ctx.details.update(cancel_sqlstate=result['sqlstate'],intermediate_indexes=[dict(name=r[0],indisvalid=r[1],indisready=r[2]) for r in rows])
    ctx.check('cancel observed as 57014',result['sqlstate']=='57014',event=result['event'])
    if recover:
        ctx.sql(ctx.admin,'DROP INDEX business_value_idx')
        ctx.sql(ctx.admin,'CREATE INDEX CONCURRENTLY business_value_idx ON business(value)')
    valid=ctx.sql(ctx.admin,"SELECT indisvalid FROM pg_index WHERE indexrelid=to_regclass('business_value_idx')")['rows']
    ctx.check('required index exists and is valid',valid==[(True,)])


def backfill(ctx, safe):
    ctx.sql(ctx.admin,'ALTER TABLE business ADD COLUMN new_value text')
    snapshot=ctx.sql(ctx.admin,'SELECT id,value FROM business ORDER BY id')['rows']
    # Copy first batch, then explicit interleaving: sustained UPDATEs before second batch/resume.
    ctx.sql(ctx.admin,'UPDATE business SET new_value=value WHERE id<=50')
    ctx.evidence.event('phase',name='backfill first batch committed; stale snapshot held')
    with ctx.cluster.connect('during_backfill') as writer:
        for key in range(1,11):
            val='changed-during-backfill-'+str(key)
            o=ctx.sql(writer,'UPDATE business SET value=%s WHERE id=%s',(val,key))
            ctx.expected[key]=val
            ctx.ledger.append(dict(op='update',id=key,value=val,event=o['event']))
    ctx.snapshot('backfill interleaving complete')
    if safe:
        ctx.sql(ctx.admin,'UPDATE business SET new_value=value')
    else:
        for key,value in snapshot:
            ctx.sql(ctx.admin,'UPDATE business SET new_value=%s WHERE id=%s',(value,key))
    mismatch=ctx.sql(ctx.admin,'SELECT id,value,new_value FROM business WHERE value IS DISTINCT FROM new_value ORDER BY id')['rows']
    ctx.details.update(intervening_updates=10,representation_mismatches=mismatch)
    ctx.check('backfilled representation equals current source',not mismatch,mismatches=mismatch)


def constraints(ctx):
    ctx.sql(ctx.admin,'CREATE TABLE parent(id int PRIMARY KEY);INSERT INTO parent VALUES(1);CREATE TABLE child(id int PRIMARY KEY,parent_id int);INSERT INTO child VALUES(1,1)')
    ctx.sql(ctx.admin,'ALTER TABLE child ADD CONSTRAINT child_parent_fk FOREIGN KEY(parent_id) REFERENCES parent(id) NOT VALID')
    before=ctx.sql(ctx.admin,"SELECT convalidated FROM pg_constraint WHERE conname='child_parent_fk'")['rows']
    ctx.sql(ctx.admin,'ALTER TABLE child VALIDATE CONSTRAINT child_parent_fk')
    ctx.sql(ctx.admin,'CREATE UNIQUE INDEX CONCURRENTLY business_unique_value ON business(value)')
    fk=ctx.sql(ctx.admin,'INSERT INTO child VALUES(2,999)',required=False)
    unique=ctx.sql(ctx.admin,"INSERT INTO business VALUES(9999,'v-1')",required=False)
    after=ctx.sql(ctx.admin,"SELECT convalidated FROM pg_constraint WHERE conname='child_parent_fk'")['rows']
    ctx.check('FK transitions NOT VALID to validated',before==[(False,)] and after==[(True,)])
    ctx.check('FK and unique constraints enforce actual writes',fk['sqlstate']=='23503' and unique['sqlstate']=='23505',events=[fk['event'],unique['event']])


def privileges(ctx,safe):
    ctx.sql(ctx.admin,'CREATE ROLE app_reader; GRANT SELECT ON business TO app_reader')
    with ctx.cluster.connect('reader_role') as reader:
        ctx.sql(reader,'SET ROLE app_reader');ctx.sql(reader,'SELECT id,value FROM business LIMIT 1');ctx.sql(reader,'RESET ROLE')
        ctx.metadata('before table replacement')
        ctx.sql(ctx.admin,'BEGIN; CREATE TABLE replacement(LIKE business INCLUDING ALL);INSERT INTO replacement SELECT * FROM business;DROP TABLE business;ALTER TABLE replacement RENAME TO business;COMMIT')
        if safe: ctx.sql(ctx.admin,'GRANT SELECT ON business TO app_reader')
        ctx.sql(reader,'SET ROLE app_reader')
        result=ctx.sql(reader,'SELECT id,value FROM business LIMIT 1',required=False)
        ctx.sql(reader,'RESET ROLE')
        ctx.details['role_sqlstate']=result['sqlstate']
        ctx.check('original role retains SELECT capability',result['ok'],event=result['event'])


def partial(ctx):
    ctx.sql(ctx.admin,'ALTER TABLE business ADD COLUMN phase1 int')
    migrator=ctx.cluster.connect('phase2');ctx.sql(migrator,'BEGIN')
    result={}
    t=ctx.fork(lambda:result.update(ctx.sql(migrator,'SELECT pg_sleep(30)',required=False)))
    ctx.wait(lambda:bool(ctx.admin.execute("SELECT 1 FROM pg_stat_activity WHERE pid=%s AND wait_event='PgSleep'",(migrator.info.backend_pid,)).fetchone()),'second transaction active')
    ctx.snapshot('before interrupting phase2');migrator.cancel_safe();ctx.join(t)
    ctx.details['transaction_status_after_cancel']=migrator.info.transaction_status.name
    ctx.sql(migrator,'ROLLBACK')
    intermediate=ctx.metadata('partial commit before resume')
    ctx.sql(ctx.admin,'ALTER TABLE business ADD COLUMN IF NOT EXISTS phase1 int;ALTER TABLE business ADD COLUMN IF NOT EXISTS phase2 int')
    cols=ctx.sql(ctx.admin,"SELECT attname FROM pg_attribute WHERE attrelid='business'::regclass AND attnum>0 AND NOT attisdropped ORDER BY attnum")['rows']
    ctx.check('explicit interrupted transaction and resumed schema',result['sqlstate']=='57014' and ctx.details['transaction_status_after_cancel']=='INERROR' and cols==[('id',),('value',),('phase1',),('phase2',)])


def execute(name,ctx):
    if name=='lock_timeout':lock_timeout(ctx)
    elif name=='concurrent_dml':concurrent_dml(ctx)
    elif name.startswith('old_new_clients_'):old_new(ctx,name.endswith('break'))
    elif name.startswith('index_'):index(ctx,name.endswith('recover'))
    elif name.startswith('backfill_'):backfill(ctx,name.endswith('safe'))
    elif name=='constraints_safe':constraints(ctx)
    elif name.startswith('privileges_'):privileges(ctx,name.endswith('safe'))
    elif name=='partial_recovery':partial(ctx)
    else:raise ValueError('Unknown scenario '+name)
