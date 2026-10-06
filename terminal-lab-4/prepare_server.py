#!/usr/bin/env python3
"""Prepare only this student's new Lab 4 folder through an existing SSH profile."""
import argparse
from pathlib import Path
import subprocess
import sys
import check
import setup


def prepare(lab_id, config):
    if not setup.valid_id(lab_id):
        raise ValueError('Invalid lab ID')
    source = (Path(__file__).resolve().parent / 'setup.py').read_text(encoding='utf-8')
    payload = f'import sys\nsys.argv = ["setup.py", "--side", "server", "--id", {lab_id!r}]\n' + source
    result = subprocess.run(check.ssh_command(config) + ['python3 -B -'], input=payload,
                            text=True, encoding='utf-8', capture_output=True, timeout=45)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or 'Server setup failed')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', required=True)
    parser.add_argument('--config', type=Path, default=Path(__file__).resolve().parent.parent / '.connection/ssh_config')
    args = parser.parse_args()
    try:
        print(prepare(args.id, args.config), end='')
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))


if __name__ == '__main__':
    main()
