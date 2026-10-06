#!/usr/bin/env python3
"""Configure this student's bundled access and prepare their roll-number attempt."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import connection
import prepare_server
import setup
import access_import


def prepare_student(root, roll_number, remote_prepare=prepare_server.prepare, access=None):
    root = setup.plain_path(Path(root).resolve())
    if not setup.valid_id(roll_number):
        raise ValueError('Enter your roll number using 1–24 letters/digits, hyphens or underscores.')
    access = setup.plain_path(access if access is not None else root / 'access')
    account_path = setup.plain_path(access / 'account.json')
    account = json.loads(account_path.read_text(encoding='utf-8'))
    fields = set(account) - {'public_key'}
    if fields not in ({'host', 'user', 'port'},{'host','user','port','host_key_alias'}):
        raise ValueError('Access package is incomplete. Ask your instructor for the correct ZIP.')
    key = setup.plain_path(access / 'ssh_key')
    known = setup.plain_path(access / 'known_hosts')
    if not key.is_file() or not known.is_file():
        raise ValueError('Missing access files. Extract the complete ZIP before starting.')
    # Some extraction tools discard ZIP permission attributes. Fix only this
    # package's own regular key file, never a global SSH file or linked target.
    key.chmod(0o600)
    config = root / '.connection/ssh_config'
    connection.configure(account['host'], account['user'], key, known, config, account['port'],account.get('host_key_alias'))
    local, created = setup.create(roll_number, 'local', root / 'lab-work')
    remote_prepare(roll_number, config)
    current = setup.plain_path(root / '.connection/current_roll')
    if current.exists() and not current.is_file():
        raise ValueError('Invalid local setup marker. Ask your instructor for help.')
    current.write_text(roll_number + '\n', encoding='utf-8')
    current.chmod(0o600)
    return local, created


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roll-number')
    parser.add_argument('--access-zip', type=Path, help='Your individual emailed access ZIP')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        # Legacy personal laptop kits still contain access/; new Codespaces
        # import a separate access-only ZIP into private storage outside Git.
        access = root / 'access' if (root / 'access').is_dir() and args.access_zip is None else access_import.install(root, args.access_zip)
        roll_number = args.roll_number or input('Enter your roll number: ').strip()
        local, created = prepare_student(root, roll_number, access=access)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        sys.exit('Setup stopped: ' + str(error))
    print('Your starting terminal and server folders are ready.' if created else 'Your existing attempt is ready. Saved work was kept.')
    print('Local folder: ' + str(local))
    print('Open Experiment_Book_4_Draft.md and begin Experiment 1.')


if __name__ == '__main__':
    main()
