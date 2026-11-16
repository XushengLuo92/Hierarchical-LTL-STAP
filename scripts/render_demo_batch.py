"""Validate and publish presentation media for the first four scenarios."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import imageio_ffmpeg
from hierarchical_ltl_stap.demo import Presentation
from hierarchical_ltl_stap.demo_monitor import Monitor


def render(scenario, folder, publish):
    stem = f'scenario_{scenario:02}'
    replay = folder/f'{stem}.json'
    data = json.loads(replay.read_text())
    validation = Monitor(data).validate()
    replay.with_suffix('.validation.json').write_text(json.dumps(validation, indent=2)+'\n')
    # Robot-robot collisions are outside this planner's scope. Report them,
    # but never change or reject an otherwise valid execution because of them.
    checks = ('planner_accepted', 'hierarchy_satisfied', 'legal_grid_paths', 'action_model_valid', 'safety_valid')
    if not all(validation[k] for k in checks):
        raise RuntimeError(f'Scenario {scenario} failed validation: {[k for k in checks if not validation[k]]}')
    view = Presentation(data)
    try:
        view.save(replay.with_suffix('.mp4'))
        view.draw(max(1, view.horizon//2))
        view.save(replay.with_suffix('.png'))
    finally:
        plt.close(view.fig)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix='hierarchical-palette-') as temp:
        palette = str(Path(temp)/'palette.png')
        subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-i', str(replay.with_suffix('.mp4')),
                        '-vf', 'fps=12,scale=960:-1:flags=lanczos,palettegen=stats_mode=diff',
                        '-frames:v', '1', palette], check=True)
        subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-i', str(replay.with_suffix('.mp4')), '-i', palette,
                        '-lavfi', 'fps=12,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3',
                        '-loop', '0', str(replay.with_suffix('.gif'))], check=True)
    frames = imageio_ffmpeg.read_frames(str(replay.with_suffix('.mp4')), pix_fmt='rgb24')
    metadata = next(frames)
    count = sum(1 for _ in frames)
    expected = math.ceil(view.horizon/2*30)+1+60
    if metadata['size'] != (1920, 1080) or count != expected:
        raise RuntimeError('Video dimensions or decoded frame count are incorrect.')
    with Image.open(replay.with_suffix('.gif')) as preview:
        if preview.size != (960, 540) or preview.n_frames < 2:
            raise RuntimeError('Invalid animated preview.')
    with Image.open(replay.with_suffix('.png')) as poster:
        if poster.size != (1920, 1080): raise RuntimeError('Invalid poster dimensions.')
    if publish:
        publish.mkdir(parents=True, exist_ok=True)
        for extension in ('.json', '.validation.json', '.mp4', '.gif', '.png'):
            shutil.copy2(replay.with_suffix(extension), publish/f'{stem}{extension}')
    return {'scenario': scenario, 'case': data['case'], 'cost_mode': data['provenance']['cost_mode'],
            'robots': len(data['robots']), 'horizon': view.horizon,
            'video': f'{stem}.mp4', 'frames': count, 'fps': 30, 'size': list(metadata['size']),
            'replay_sha256': hashlib.sha256(replay.read_bytes()).hexdigest(),
            'checks': {k: validation[k] for k in checks}, 'collision_avoidance': False,
            'collision_diagnostics': {'collision_free': validation['collision_free'],
                                      'conflict_count': len(validation['conflicts'])}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenarios', nargs='+', type=int, choices=range(1, 5), default=list(range(1, 5)))
    parser.add_argument('--output-dir', type=Path, default=ROOT/'data/first_four')
    parser.add_argument('--publish-dir', type=Path, default=ROOT/'demo/generated')
    args = parser.parse_args()
    manifest = args.output_dir/'rendered.json'
    rows = {r['scenario']: r for r in json.loads(manifest.read_text())} if manifest.exists() else {}
    for scenario in args.scenarios:
        print(f'Rendering Scenario {scenario}', flush=True)
        rows[scenario] = render(scenario, args.output_dir, args.publish_dir)
        manifest.write_text(json.dumps(sorted(rows.values(), key=lambda r: r['scenario']), indent=2)+'\n')
        print(f'Scenario {scenario}: video, preview, poster and replay verified.', flush=True)
    if args.publish_dir:
        shutil.copy2(manifest, args.publish_dir/manifest.name)


if __name__ == '__main__':
    main()
