"""CLI: 0 PASS, 2 FAIL/INCONCLUSIVE or invalid evidence, 1 input/environment error."""
import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
    parser=argparse.ArgumentParser(description='Disposable PostgreSQL migration reliability experiments')
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('list')
    p=sub.add_parser('run')
    p.add_argument('scenario',help='Built-in name or trusted JSON file')
    p.add_argument('--pg-bin',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--allow-trusted-command',action='store_true',help='Execute explicitly supplied argv outside any OS sandbox')
    for name in ('verify','render'):
        p=sub.add_parser(name);p.add_argument('directory',type=Path)
    args=parser.parse_args(argv)
    try:
        if args.action=='list':
            from .scenarios import CONTROLS
            print(json.dumps(CONTROLS,indent=2));return 0
        if args.action=='verify':
            from .evidence import verify
            errors=verify(args.directory)
            print(json.dumps(dict(valid=not errors,errors=errors),ensure_ascii=False));return 2 if errors else 0
        if args.action=='render':
            from .evidence import render
            render(args.directory);print('Rendered unsealed evidence');return 0
        from .runner import run
        from .custom import load_case
        scenario=load_case(args.scenario) if Path(args.scenario).is_file() else args.scenario
        result=run(scenario,args.pg_bin,args.output,allow_command=args.allow_trusted_command)
        print(json.dumps(result,indent=2,ensure_ascii=False,default=str))
        return 0 if result['outcome']=='PASS' else 1 if result['outcome']=='ERROR' else 2
    except (ValueError,OSError,RuntimeError) as e:
        print(json.dumps(dict(error=str(e)),ensure_ascii=False),file=sys.stderr);return 1
