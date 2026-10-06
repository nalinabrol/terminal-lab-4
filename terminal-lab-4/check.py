#!/usr/bin/env python3
"""Read-only feedback on local deliverables and actual remote file modes."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tarfile
import zipfile
import setup

UPLOAD = b'Prepared in my starting terminal\n'
EDITED = UPLOAD + b'Edited on the server\n'
UPLOAD_WINDOWS = UPLOAD.replace(b'\n', b'\r\n')
EDITED_WINDOWS = UPLOAD_WINDOWS + b'Edited on the server\n'
LIMIT = 256 * 1024


def read(root, name):
    """Reject links, special files and oversized files before opening."""
    root = setup.plain_path(root)
    path = setup.plain_path(root / name)
    if not path.is_relative_to(root):
        raise ValueError('Path leaves the lab folder')
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
        raise ValueError('Expected a small regular file')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0))
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Expected a regular file')
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('File is too large')
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive_valid(data, kind, lab_id):
    expected = {'project/' + name: value for name, value in setup.project(lab_id).items()}
    found = {}
    names = set()
    if kind == 'zip':
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > 8:
                return False
            for member in members:
                name = member.filename.replace('\\', '/')
                if name in names:
                    return False
                names.add(name)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode):
                    return False
                if name.endswith('/'):
                    if name != 'project/' or member.file_size != 0:
                        return False
                elif name not in expected or member.file_size > LIMIT or stat.S_ISLNK(mode):
                    return False
                else:
                    found[name] = archive.read(member)
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            for index, member in enumerate(archive):
                if index >= 8 or member.name in names:
                    return False
                names.add(member.name)
                if member.isdir():
                    if member.name.rstrip('/') != 'project':
                        return False
                elif not member.isfile() or member.name not in expected or member.size > LIMIT:
                    return False
                else:
                    found[member.name] = archive.extractfile(member).read(LIMIT + 1)
    return found == expected


def originals_ok(root, lab_id, side):
    return all(read(root, name) == data for name, data in setup.originals(lab_id, side).items())


def mode_ok(root, name, mode):
    read(root, name)
    info = (root / name).lstat()
    return stat.S_IMODE(info.st_mode) == mode and info.st_uid == os.getuid()


def report_ok(root, lab_id):
    import pwd
    owner = pwd.getpwuid(os.getuid()).pw_name
    expected = {'announcement.txt': '-rw-r--r--', 'planning-notes.txt': '-rw-------',
                'hello.sh': '-rwx------'}
    found = {}
    for line in read(root, 'challenge-delivery/permissions-report.txt').decode().splitlines():
        if line.startswith('total '):
            continue
        fields = line.split()
        if len(fields) < 9 or fields[-1] not in expected or fields[-1] in found:
            return False
        name = fields[-1]
        if fields[0].rstrip('@') != expected[name] or fields[2] != owner:
            return False
        if int(fields[4]) != len(setup.project(lab_id)[name]):
            return False
        found[name] = fields[0].rstrip('@')
    return found == expected


def evaluate_server(root, lab_id):
    results = []
    evidence = {}

    def test(label, operation):
        try:
            ok = bool(operation())
        except (OSError, ValueError, UnicodeError, zipfile.BadZipFile, tarfile.TarError, RuntimeError):
            ok = False
        results.append({'label': label, 'ok': ok})

    test('Server originals unchanged', lambda: originals_ok(root, lab_id, 'server'))
    test('Server connected.txt exists and is empty', lambda: read(root, 'connected.txt') == b'')
    test('Owner-write exercise saved one extra line', lambda: read(root, 'work/notes.txt') == setup.practice(lab_id)['notes.txt'] + b'An extra note\n')
    for name, mode in [('notes.txt', 0o660), ('hello.sh', 0o700), ('private.txt', 0o600),
                       ('announcement.txt', 0o644), ('team-notes.txt', 0o660)]:
        test(f'Server work/{name} mode {mode:o}, owned by this user',
             lambda name=name, mode=mode: mode_ok(root, 'work/' + name, mode))
    test('Other working fixture contents unchanged', lambda: all(
        read(root, 'work/' + name) == data for name, data in setup.practice(lab_id).items()
        if name != 'notes.txt'))
    test('Server uploaded file contains the server edit', lambda: read(root, 'work/upload.txt') in (EDITED, EDITED_WINDOWS))
    for name, mode in [('announcement.txt', 0o644), ('planning-notes.txt', 0o600), ('hello.sh', 0o700)]:
        test(f'Delivered {name}: correct bytes, mode {mode:o}, owned by this user',
             lambda name=name, mode=mode: read(root, 'challenge-delivery/project/' + name) == setup.project(lab_id)[name]
             and mode_ok(root, 'challenge-delivery/project/' + name, mode))
    test('Uploaded challenge archive contains exactly the original project', lambda: any(
        archive_valid(read(root, 'challenge-delivery/' + name), kind, lab_id)
        for name, kind in available_archives(root / 'challenge-delivery')))
    test('Server report names all three files with their required modes and owner', lambda: report_ok(root, lab_id))
    for name in ['work/upload.txt', 'challenge-delivery/permissions-report.txt', 'challenge-delivery/project.zip', 'challenge-delivery/project.tar.gz']:
        try:
            evidence[name] = digest(read(root, name))
        except (OSError, ValueError):
            pass
    return {'side': 'server', 'lab_id': lab_id, 'results': results, 'evidence': evidence}


def available_archives(folder):
    return [(name, kind) for name, kind in [('project.zip', 'zip'), ('project.tar.gz', 'tar')]
            if (folder / name).exists() or (folder / name).is_symlink()]


def evaluate_local(root, lab_id, remote):
    results = []

    def test(label, operation):
        try:
            ok = bool(operation())
        except (OSError, ValueError, UnicodeError, zipfile.BadZipFile, tarfile.TarError, RuntimeError):
            ok = False
        results.append({'label': label, 'ok': ok})

    test('Starting-machine originals unchanged', lambda: originals_ok(root, lab_id, 'local'))
    test('Starting-machine upload remains the original one-line file', lambda: read(root, 'work/upload.txt') in (UPLOAD, UPLOAD_WINDOWS))
    test('Downloaded upload includes the server edit', lambda: read(root, 'work/recovered/upload.txt') in (EDITED, EDITED_WINDOWS)
         and digest(read(root, 'work/recovered/upload.txt')) == remote['evidence'].get('work/upload.txt'))
    test('connected.txt is absent on the starting machine', lambda: not (root / 'connected.txt').exists() and not (root / 'connected.txt').is_symlink())
    test('Local archive is valid and matches an uploaded server archive', lambda: any(
        archive_valid(read(root, 'work/' + name), kind, lab_id)
        and digest(read(root, 'work/' + name)) == remote['evidence'].get('challenge-delivery/' + name)
        for name, kind in available_archives(root / 'work')))
    test('Downloaded permissions report matches the server report', lambda: bool(remote['evidence'].get('challenge-delivery/permissions-report.txt'))
         and digest(read(root, 'work/permissions-report.txt')) == remote['evidence']['challenge-delivery/permissions-report.txt'])
    return results


def remote_source(lab_id):
    """Execute checker in memory; install or modify nothing on the server."""
    kit = Path(__file__).resolve().parent
    return ('import sys, types\n'
            'm = types.ModuleType("setup")\nsys.modules["setup"] = m\n'
            f'exec({(kit / "setup.py").read_text(encoding="utf-8")!r}, m.__dict__)\n'
            f'sys.argv = ["check.py", "--side", "server", "--id", {lab_id!r}, "--json"]\n'
            f'exec({(kit / "check.py").read_text(encoding="utf-8")!r}, {{"__name__": "__main__"}})\n')


def ssh_command(config):
    return ['ssh', '-F', str(Path(config).resolve()), '-o', 'BatchMode=yes',
            '-o', 'ConnectTimeout=12', 'lab-server']


def fetch_remote(lab_id, config):
    process = subprocess.run(ssh_command(config) + ['python3 -B -'], input=remote_source(lab_id),
                             text=True, encoding='utf-8', capture_output=True, timeout=45)
    if process.returncode not in (0, 1):
        raise ValueError('Could not inspect the server: ' + process.stderr.strip())
    payload = json.loads(process.stdout)
    if payload.get('side') != 'server' or payload.get('lab_id') != lab_id:
        raise ValueError('Unexpected server checker response')
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--side', choices=('local', 'server'), default='local')
    parser.add_argument('--id')
    parser.add_argument('--root', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        if args.side == 'server':
            if not args.id or not setup.valid_id(args.id):
                raise ValueError('A valid server lab ID is required')
            root = args.root or Path.home() / 'work' / ('lab4-' + args.id)
            result = evaluate_server(root, args.id)
        else:
            root = setup.plain_path(args.root or Path.cwd())
            match = re.fullmatch(rb'LAB_ID=([A-Za-z0-9_-]+)\nDATA_VERSION=lab4-v1\nSIDE=local\n', read(root, 'identity.txt'))
            if not match:
                raise ValueError('Run this checker from your starting-machine Lab 4 folder')
            lab_id = match.group(1).decode()
            if not setup.valid_id(lab_id):
                raise ValueError('Invalid lab identity')
            config = args.config or Path(__file__).resolve().parent.parent / '.connection/ssh_config'
            remote = fetch_remote(lab_id, config)
            result = {'side': 'local', 'lab_id': lab_id,
                      'results': evaluate_local(root, lab_id, remote) + remote['results']}
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('CHECK: ' + str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result))
    else:
        for item in result['results']:
            print(('PASS: ' if item['ok'] else 'CHECK: ') + item['label'])
        print(f"{sum(item['ok'] for item in result['results'])}/{len(result['results'])} checks passed.")
        print('File checks do not grade explanations or prove independent interactive work.')
    return 0 if all(item['ok'] for item in result['results']) else 1


if __name__ == '__main__':
    sys.exit(main())
