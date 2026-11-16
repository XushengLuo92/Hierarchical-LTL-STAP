"""Export the demo's office map at the recorded initial robot positions."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hierarchical_ltl_stap.demo import BG, Presentation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, default=ROOT/'demo/generated/scenario_01.json')
    parser.add_argument('--output', type=Path, default=ROOT/'demo/generated/environment.png')
    args = parser.parse_args()
    view = Presentation(json.loads(args.replay.read_text()))
    try:
        view.draw(0)
        view.fig.canvas.draw()
        bounds = view.ax.get_window_extent().transformed(view.fig.dpi_scale_trans.inverted())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        view.fig.savefig(args.output, dpi=160, facecolor=BG, bbox_inches=bounds.expanded(1.025, 1.1))
        print(f'Saved {args.output}')
    finally:
        plt.close(view.fig)


if __name__ == '__main__':
    main()
