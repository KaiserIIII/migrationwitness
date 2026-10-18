"""Breaks caught: accepting existing data/DSN, root initdb, missing binaries."""
import os
from pathlib import Path
import pytest


def test_missing_binary_directory_refused(tmp_path):
    from migrationwitness.cluster import Cluster
    with pytest.raises(ValueError, match='executables'):
        Cluster(tmp_path)


def test_root_cannot_initialize(pg_bin):
    from migrationwitness.cluster import Cluster
    if not hasattr(os,'geteuid') or os.geteuid()!=0:
        pytest.skip('Only root refusal branch')
    with pytest.raises(ValueError, match='root'):
        with Cluster(pg_bin):
            pass


def test_cluster_owns_disposable_database_and_stops(pg_bin, tmp_path):
    from migrationwitness.cluster import Cluster
    if hasattr(os,'geteuid') and os.geteuid()==0:
        pytest.skip('Run integration as non-root')
    c=Cluster(pg_bin)
    with c:
        owned=c.root
        with c.connect() as db:
            assert db.execute('select current_database(),current_user').fetchone()==('mw_test','mw_owner')
            assert db.execute('show listen_addresses').fetchone()[0]=='' if os.name!='nt' else True
        assert owned.is_dir()
    assert not owned.exists()


def test_logging_failure_after_start_still_stops_owned_postmaster(pg_bin):
    from migrationwitness.cluster import Cluster
    if hasattr(os,'geteuid') and os.geteuid()==0:pytest.skip('Unprivileged initdb required')
    class Fault:
        pid=None
        def event(self,kind,**fields):
            argv=fields.get('argv',[])
            if argv and argv[-1]=='start' and fields['returncode']==0:
                data=Path(argv[argv.index('-D')+1])
                self.pid=int((data/'postmaster.pid').read_text().splitlines()[0])
                raise OSError('simulated evidence write failure')
        def write_json(self,*args):pass
    fault=Fault();cluster=Cluster(pg_bin,fault)
    with pytest.raises(OSError):
        with cluster:pass
    assert fault.pid is not None
    with pytest.raises(ProcessLookupError):os.kill(fault.pid,0)

