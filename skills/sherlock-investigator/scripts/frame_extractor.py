"""Bounded deterministic sampling (not semantic keyframe detection)."""
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def extract_frames(path, count=5, interval=2.0, timeout=60):
    if not 1 <= count <= 20 or not 0.1 <= interval <= 600:
        raise ValueError('Frame limits: count 1..20, interval 0.1..600 seconds')
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('ffmpeg unavailable; ask the host agent for supported video tooling')
    source = Path(path).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='sherlock-frames-') as folder:
        pattern = str(Path(folder) / 'frame-%03d.jpg')
        command = [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error',
                   '-protocol_whitelist', 'file,pipe', '-threads', '1', '-i', str(source),
                   '-vf', f'fps=1/{interval},scale=1280:1280:force_original_aspect_ratio=decrease',
                   '-frames:v', str(count), '-threads', '1', pattern]
        try:
            subprocess.run(command, check=True, timeout=timeout, capture_output=True)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError('ffmpeg could not decode this input') from exc
        files = sorted(Path(folder).glob('frame-*.jpg'))
        if not files:
            raise RuntimeError('No frames decoded; reduce interval for short clips')
        yield [{'path': str(p), 'timestamp_seconds_approx': i * interval,
                'method': 'uniform_sample', 'original': False} for i, p in enumerate(files)]
