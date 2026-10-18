"""Run selected native controls in NEW clusters; never reuse/overwrite evidence.

Example: python scripts/acceptance.py --pg-bin /usr/lib/postgresql/17/bin --output runs/acceptance-17 --repeat 3
Run as an unprivileged user. This does not install PostgreSQL or contact a remote DB.
"""
import argparse
import json
from pathlib import Path
from migrationwitness.runner import run
from migrationwitness.scenarios import CONTROLS
from migrationwitness.evidence import verify

p=argparse.ArgumentParser()
p.add_argument('--pg-bin',required=True,type=Path)
p.add_argument('--output',required=True,type=Path)
p.add_argument('--repeat',type=int,default=1,choices=range(1,6))
args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=False)
records=[]
for repeat in range(args.repeat):
    for name in CONTROLS:
        out=args.output/f'{repeat}-{name}'
        r=run(name,args.pg_bin,out)
        record=dict(scenario=name,repeat=repeat,outcome=r['outcome'],agreement=r['control_agreement'],elapsed_s=r['elapsed_s'],evidence_valid=not verify(out))
        records.append(record)
        print(json.dumps(record),flush=True)
summary=dict(selected_controls=records,agreement=sum(r['agreement'] for r in records),total=len(records),evidence_all_valid=all(r['evidence_valid'] for r in records))
(args.output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
raise SystemExit(0 if summary['agreement']==summary['total'] and summary['evidence_all_valid'] else 1)
