"""Reproduce the first four README scenarios with real planner executions."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = {1: 12, 2: 13, 3: 14, 4: 21}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenarios', nargs='+', type=int, choices=CASES, default=list(CASES))
    parser.add_argument('--output-dir', type=Path, default=ROOT/'data/first_four')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--cost', choices=('min', 'minmax'), default='minmax',
                        help='Planner objective (default: minmax)')
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()
    folder = args.output_dir.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    manifest = folder/'planning.json'
    rows = {r['scenario']: r for r in json.loads(manifest.read_text())} if manifest.exists() else {}
    for scenario in args.scenarios:
        replay = folder/f'scenario_{scenario:02}.json'
        command = [sys.executable, '-u', str(ROOT/'hierarchical_LTL_stap_on_the_fly.py'),
                   '--task=nav', f'--case={CASES[scenario]}', '--heuristics', '--heuristic_weight=100',
                   '--domain_file=domain/domain_bosch.json', '--domain=bosch', '--num_robots=6',
                   f'--cost={args.cost}', f'--seed={args.seed}', '--print_step',
                   '--replay-output', str(replay)]
        start = time.time()
        print(f'Planning Scenario {scenario} (case {CASES[scenario]})', flush=True)
        with (folder/f'scenario_{scenario:02}.log').open('w') as log:
            try:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, 'PYTHONHASHSEED': '0', 'MPLBACKEND': 'Agg'},
                                        timeout=args.timeout)
                success = result.returncode == 0 and replay.exists() and replay.stat().st_mtime >= start
                status = 'planned' if success else 'failed'
            except subprocess.TimeoutExpired:
                status = 'timeout'
        rows[scenario] = {'scenario': scenario, 'case': CASES[scenario], 'status': status,
                          'seconds': round(time.time()-start, 2), 'command': command}
        manifest.write_text(json.dumps(sorted(rows.values(), key=lambda r: r['scenario']), indent=2)+'\n')
        print(rows[scenario], flush=True)
        if status != 'planned':
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
