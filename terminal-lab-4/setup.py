#!/usr/bin/env python3
"""Create deterministic Lab 4 attempts; preserve every existing attempt."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import sys

VERSION = 'lab4-v1'
NAMES = ('notes.txt', 'private.txt', 'announcement.txt', 'team-notes.txt', 'hello.sh')


def valid_id(value):
    return re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,23}', value) is not None


def project(lab_id):
    if not valid_id(lab_id):
        raise ValueError('Use 1–24 letters/digits, hyphens or underscores; begin with a letter/digit.')
    return {
        'announcement.txt': f'Campus showcase — {lab_id}\nDoors open at 10:00.\n'.encode(),
        'planning-notes.txt': f'Private planning notes — {lab_id}\nPrepare the display before opening.\n'.encode(),
        'hello.sh': f'#!/bin/sh\nprintf "%s\\n" "Project delivered for {lab_id}."\n'.encode(),
    }


def identity(lab_id, side):
    return f'LAB_ID={lab_id}\nDATA_VERSION={VERSION}\nSIDE={side}\n'.encode()


def practice(lab_id):
    return {
        'notes.txt': f'Lab notes for {lab_id}.\n'.encode(),
        'private.txt': f'Private note for {lab_id}.\n'.encode(),
        'announcement.txt': f'Announcement for {lab_id}.\n'.encode(),
        'team-notes.txt': f'Team notes for {lab_id}.\n'.encode(),
        'hello.sh': f'#!/bin/sh\nprintf "%s\\n" "Hello from Lab 4, {lab_id}."\n'.encode(),
    }


def originals(lab_id, side):
    project(lab_id)  # Validate even when this side has no challenge tree.
    files = {'identity.txt': identity(lab_id, side)}
    files.update({'practice/' + name: data for name, data in practice(lab_id).items()})
    if side == 'local':
        files.update({'challenge/project/' + name: data for name, data in project(lab_id).items()})
    elif side != 'server':
        raise ValueError('Unknown side')
    return files


def plain_path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('A lab path contains a symbolic link. Use a real directory.')
    return path


def create(lab_id, side, base):
    files = originals(lab_id, side)
    base = plain_path(base)
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    root = plain_path(base / ('lab4-' + lab_id))
    if root.exists():
        if not root.is_dir() or (root / 'identity.txt').is_symlink():
            raise ValueError('Existing attempt is not a valid lab folder. Use a new ID.')
        if (root / 'identity.txt').read_bytes() != identity(lab_id, side):
            raise ValueError('Existing attempt has a different identity/version. Use a new ID.')
        return root, False
    root.mkdir(mode=0o700)
    for name, data in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with target.open('xb') as out:
            out.write(data)
        target.chmod(0o600)
    (root / 'work').mkdir(mode=0o700)
    if side == 'server':
        for name, data in practice(lab_id).items():
            target = root / 'work' / name
            with target.open('xb') as out:
                out.write(data)
            target.chmod(0o644 if name == 'notes.txt' else 0o600)
    return root, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id')
    parser.add_argument('--side', choices=('local', 'server'), default='local')
    parser.add_argument('--base', type=Path)
    args = parser.parse_args()
    lab_id = args.id or input('Enter your roll number: ').strip()
    base = args.base or (Path.home() / 'work' if args.side == 'server'
                         else Path(__file__).resolve().parent.parent / 'lab-work')
    try:
        root, created = create(lab_id, args.side, base)
    except (ValueError, OSError) as error:
        sys.exit(str(error))
    print('Created your Lab 4 folder.' if created else 'Existing attempt preserved. Nothing was reset.')
    print('cd ' + shlex.quote(str(root)))
    print('Then run: pwd; cat identity.txt')


if __name__ == '__main__':
    main()
