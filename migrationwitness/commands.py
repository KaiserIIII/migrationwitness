"""Trusted subprocesses only. This is not an OS security sandbox."""
import os
import base64
import signal
import subprocess
import threading
import time


def execute_command(argv, env, *, allowed=False, timeout=20, output_limit=1_000_000):
    if not allowed:
        raise ValueError('Explicit trusted command opt-in is required')
    if not isinstance(argv,list) or not argv or len(argv)>64 or not all(isinstance(x,str) and '\0' not in x and len(x)<65536 for x in argv):
        raise ValueError('Command must be a nonempty string argv list')
    if not 0<timeout<=40 or not 1<=output_limit<=1_000_000:
        raise ValueError('Command resource limit outside allowed range')
    start=time.monotonic()
    effective_env=dict(os.environ if env is None else env)
    effective_env.update(PYTHONIOENCODING='utf-8',PYTHONUTF8='1')
    p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                       env=effective_env,shell=False,start_new_session=(os.name!='nt'))
    buffers=[bytearray(),bytearray()]
    over=threading.Event()
    def read(pipe,buf):
        while True:
            chunk=pipe.read(4096)
            if not chunk:break
            space=output_limit-len(buf)
            buf.extend(chunk[:space])
            if len(chunk)>space:over.set()
    threads=[threading.Thread(target=read,args=(pipe,buf),daemon=True) for pipe,buf in zip((p.stdout,p.stderr),buffers)]
    for t in threads:t.start()
    timed=False
    while p.poll() is None:
        if over.is_set() or time.monotonic()-start>timeout:
            timed=not over.is_set()
            if os.name=='nt':p.kill()
            else:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            break
        time.sleep(.01)
    p.wait(timeout=5)
    descendants=False
    if os.name!='nt':
        try:
            os.killpg(p.pid,0)
            os.killpg(p.pid,signal.SIGKILL)
            descendants=True
        except ProcessLookupError:pass
    for t in threads:t.join(1)
    # Detached descendants can retain pipes; do not label incomplete capture as success.
    incomplete=any(t.is_alive() for t in threads)
    if not incomplete:
        p.stdout.close();p.stderr.close()
    decode_errors=False
    for buf in buffers:
        try:buf.decode('utf8')
        except UnicodeDecodeError:decode_errors=True
    return dict(argv=argv,returncode=p.returncode,stdout=buffers[0].decode('utf8',errors='replace'),
                stderr=buffers[1].decode('utf8',errors='replace'),timed_out=timed,
                stdout_base64=base64.b64encode(buffers[0]).decode('ascii'),stderr_base64=base64.b64encode(buffers[1]).decode('ascii'),decode_errors=decode_errors,
                truncated=over.is_set(),capture_incomplete=incomplete,descendants_terminated=descendants,elapsed_s=time.monotonic()-start)
