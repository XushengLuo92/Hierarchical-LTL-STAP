"""Make README media from the original AI2THOR recording (no simulation rerun)."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import imageio_ffmpeg

SOURCE_URL = 'https://github.com/user-attachments/assets/d52152d0-2622-4db9-a8fc-1ba5a882ae21'
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Downloaded original AI2THOR recording')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'demo/generated')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    video = args.output_dir/'ai2thor.mp4'
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def run(*command):
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', *map(str, command)], check=True)

    # The original is HEVC in a QuickTime container. Use H.264 for previews
    # while retaining the original size, frame rate, duration, and AAC audio.
    run('-i', args.source, '-map', '0:v:0', '-map', '0:a?', '-c:v', 'libx264',
        '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
        '-movflags', '+faststart', video)
    run('-ss', '2', '-i', video, '-frames:v', '1', args.output_dir/'ai2thor.png')
    with tempfile.TemporaryDirectory(prefix='ai2thor-palette-') as temp:
        palette = Path(temp)/'palette.png'
        run('-i', video, '-vf', 'fps=12,scale=720:-1:flags=lanczos,palettegen=stats_mode=diff',
            '-frames:v', '1', palette)
        run('-i', video, '-i', palette, '-lavfi',
            'fps=12,scale=720:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3',
            '-loop', '0', args.output_dir/'ai2thor.gif')
    counts, metadata = [], []
    for path in (args.source, video):
        frames = imageio_ffmpeg.read_frames(str(path), pix_fmt='rgb24')
        metadata.append(next(frames))
        counts.append(sum(1 for _ in frames))
    assert counts[0] == counts[1]
    assert metadata[0]['size'] == metadata[1]['size']
    assert metadata[0]['fps'] == metadata[1]['fps']
    record = {'source_url': SOURCE_URL, 'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
              'video_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
              'source': 'original AI2THOR demonstration, not a new planner run',
              'video_codec': 'H.264', 'frames': counts[1], 'fps': metadata[1]['fps'],
              'size': metadata[1]['size'], 'duration_seconds': metadata[1]['duration']}
    (args.output_dir/'ai2thor.source.json').write_text(json.dumps(record, indent=2)+'\n')
    print(f'Verified {counts[1]} frames; saved AI2THOR MP4, GIF, and poster.', flush=True)


if __name__ == '__main__':
    main()
