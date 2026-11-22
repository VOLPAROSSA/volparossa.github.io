#!/usr/bin/env python3
"""Refresh the worktable's transparent perspective layers with ImageMagick 7."""
import subprocess

from build_site import ROOT, SCREENS, screen_bounds


def prepare(ident, size, corners):
    # Keep detail at desktop and Retina sizes. Layout uses the original coordinates.
    scale = 2
    width, height = (value * scale for value in size)
    left, top, box_width, box_height = screen_bounds(corners)
    source = [(0, 0), (width, 0), (width, height), (0, height)]
    mappings = [
        f'{u},{v} {(x - left) * scale},{(y - top) * scale}'
        for (u, v), (x, y) in zip(source, corners)
    ]
    upstream = ROOT / 'assets/upstream'
    background = {'code': '#121212', 'image': '#000000', 'cloud': '#ffffff'}[ident]
    mask = ['(', '-size', f'{width}x{height}', 'xc:black', '-fill', 'white',
            '-draw', f'roundrectangle 0,0 {width-1},{height-1} {3*scale},{3*scale}']
    if ident == 'image':
        # The camera in front of the tablet hides its lower right corner.
        mask += ['-fill', 'black', '-draw',
                 f'polygon {width},{height*.88} {width*.98},{height*.92} {width*.97},{height} {width},{height}']
    mask += [')', '-alpha', 'off', '-compose', 'CopyAlpha', '-composite']
    subprocess.run([
        'magick', str(upstream / f'{ident}-screen.webp'),
        '-resize', f'{width}x{height}', '-background', background,
        '-gravity', 'north' if ident == 'cloud' else 'center', '-extent', f'{width}x{height}',
        '+repage', *mask, '-virtual-pixel', 'transparent',
        '-define', f'distort:viewport={box_width*scale}x{box_height*scale}+0+0',
        '-distort', 'Perspective', ' '.join(mappings), '+repage', '-strip',
        '-define', 'webp:method=6', '-quality', '94', str(upstream / f'{ident}-worktable.webp')
    ], check=True)


if __name__ == '__main__':
    for name, (size, corners) in SCREENS.items():
        prepare(name, size, corners)
