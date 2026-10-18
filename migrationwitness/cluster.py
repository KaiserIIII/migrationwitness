"""Own a fresh local cluster. There is deliberately no existing-DSN constructor."""
from __future__ import annotations
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import tempfile
import psycopg


class Cluster:
    def __init__(self, pg_bin: Path, evidence=None):
        self.bin = Path(pg_bin).resolve()
        suffix = '.exe' if os.name == 'nt' else ''
        self.executables = {n: self.bin/(n+suffix) for n in ('initdb','pg_ctl','postgres')}
        if not all(p.is_file() for p in self.executables.values()):
            raise ValueError('Missing PostgreSQL executables: initdb, pg_ctl, postgres')
        self.evidence = evidence
        self.root = None
        self._started = False
        self._connections = []
        self._token = secrets.token_hex(16)

    def _command(self, argv):
        p = subprocess.run([str(x) for x in argv], capture_output=True, text=True,
                           encoding='utf8', errors='replace', timeout=35)
        if self.evidence:
            # Generated data directories contain no caller secrets; password file contents excluded.
            self.evidence.event('cluster_command', argv=[str(x) for x in argv],
                                returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
        if p.returncode:
            raise RuntimeError('PostgreSQL lifecycle command failed: '+p.stderr)
        return p

    def __enter__(self):
        if hasattr(os,'geteuid') and os.geteuid()==0:
            raise ValueError('Do not run PostgreSQL initdb as root; use a dedicated unprivileged user')
        self.root = Path(tempfile.mkdtemp(prefix='mw-'))
        (self.root/'owner').write_text(self._token, encoding='ascii')
        data = self.root/'data'
        try:
            self._command([self.executables['initdb'],'-D',data,'--username=mw_owner',
                           '--auth-local=trust','--auth-host=reject','--no-locale','--encoding=UTF8'])
            # Linux uses a private mode-0700 Unix socket, no TCP listener.
            if os.name == 'nt':
                with socket.socket() as s:
                    s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
                password=secrets.token_hex(24)
                # Windows native execution is supported but requires separate acceptance.
                (data/'pg_hba.conf').write_text('host all all 127.0.0.1/32 scram-sha-256\n',encoding='ascii')
                # Bootstrap auth only for the generated private cluster via a one-use startup option.
                # Avoid native TCP until a password can be set through a safe local channel.
                raise ValueError('Native Windows cluster lifecycle not accepted; run PostgreSQL in WSL/Linux')
            else:
                self._kwargs = dict(host=str(self.root), port=5432, dbname='mw_test', user='mw_owner')
                config = "\nlisten_addresses=''\nunix_socket_directories='"+str(self.root)+"'\n"
            config += "shared_buffers='32MB'\nmax_connections=20\nmax_worker_processes=2\nmax_parallel_workers=1\nmax_parallel_maintenance_workers=0\nlog_min_error_statement=error\nlog_error_verbosity=verbose\nlog_lock_waits=on\ndeadlock_timeout='100ms'\n"
            with (data/'postgresql.conf').open('a',encoding='utf8') as f:
                f.write(config)
            # Once start is attempted it may have succeeded even if output/evidence I/O fails.
            # Always attempt stop before any directory cleanup on this path.
            self._started=True
            self._command([self.executables['pg_ctl'],'-D',data,'-l',self.root/'server.log','-w','start'])
            with psycopg.connect(**(self._kwargs | {'dbname':'postgres'}),autocommit=True) as c:
                c.execute('CREATE DATABASE mw_test')
            return self
        except BaseException:
            self.__exit__(None,None,None)
            raise

    def connect(self, name='client', autocommit=True):
        if not self._started:
            raise RuntimeError('Cluster not running')
        c=psycopg.connect(**self._kwargs,autocommit=autocommit,connect_timeout=5,
                         application_name='mw_'+name,
                         options='-c statement_timeout=10000 -c lock_timeout=2000 -c idle_in_transaction_session_timeout=20000')
        self._connections.append(c)
        return c

    def command_env(self):
        """Ephemeral connection env, only for explicitly trusted subprocesses."""
        if not self._started:
            raise RuntimeError('Cluster not running')
        env={k:v for k,v in os.environ.items() if not k.startswith('PG')}
        env.update(PGHOST=str(self.root),PGPORT='5432',PGDATABASE='mw_test',PGUSER='mw_owner',
                   PGSSLMODE='disable',PGCONNECT_TIMEOUT='5',PGOPTIONS='-c statement_timeout=10000 -c lock_timeout=2000')
        env['PATH']=str(self.bin)+os.pathsep+env.get('PATH','')
        return env

    def __exit__(self,*exc):
        for c in self._connections:
            c.close()
        failure=None
        if self.root and self._started:
            try:
                self._command([self.executables['pg_ctl'],'-D',self.root/'data','-m','immediate','-w','stop'])
            except Exception as e:
                failure=e
            finally:
                if self.evidence and (self.root/'server.log').exists():
                    self.evidence.write_json('postgres-log.json',{'text':(self.root/'server.log').read_text(encoding='utf8',errors='replace')})
        # Remove only our tempfile after a successful stop, with immutable ownership token.
        if self.root and failure is None:
            if self.root.parent.resolve()!=Path(tempfile.gettempdir()).resolve() or not self.root.name.startswith('mw-') or (self.root/'owner').read_text()!=self._token:
                raise RuntimeError('Refusing cleanup: cluster ownership mismatch')
            shutil.rmtree(self.root)
        self._started=False
        if failure:
            raise RuntimeError('Cluster stop failed; retained '+str(self.root)) from failure
