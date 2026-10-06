#!/usr/bin/env python3
"""Import one emailed access ZIP without extracting arbitrary archive paths."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
import setup

ACCESS_FILES = {'account.json', 'ssh_key', 'known_hosts'}


def read_archive(path):
    path = setup.plain_path(path)
    if not path.is_file() or path.stat().st_size > 262144:
        raise ValueError('Upload your individual Lab 4 access ZIP, not a class bundle.')
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            roots = {name.split('/')[0] for name in names}
            if len(roots) != 1:
                raise ValueError('Expected one account in the access ZIP.')
            prefix = next(iter(roots))
            match = re.fullmatch(r'Lab_4_(student[0-9]{2,3})_Access', prefix)
            expected = {prefix + '/README.md'} | {prefix + '/access/' + name for name in ACCESS_FILES}
            if not match or len(names) != 4 or set(names) != expected:
                raise ValueError('Use the access-only ZIP emailed by your instructor.')
            for entry in archive.infolist():
                kind = stat.S_IFMT(entry.external_attr >> 16)
                if entry.file_size > 65536 or kind not in (0, stat.S_IFREG) or entry.flag_bits & 1:
                    raise ValueError('The access ZIP contains an unsupported file.')
            data = {name: archive.read(prefix + '/access/' + name) for name in ACCESS_FILES}
    except (zipfile.BadZipFile, RuntimeError) as error:
        raise ValueError('Cannot read the access ZIP. Upload the original emailed file.') from error
    try:
        account = json.loads(data['account.json'])
    except (ValueError, UnicodeError) as error:
        raise ValueError('Invalid account details in the access ZIP.') from error
    required = {'host', 'user', 'port', 'public_key'}
    if (not isinstance(account, dict) or set(account) not in (required, required | {'host_key_alias'})
            or account['user'] != match.group(1)
            or not isinstance(account['host'], str)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', account['host'])
            or type(account['port']) is not int or not 1 <= account['port'] <= 65535
            or not isinstance(account['public_key'], str)
            or len(account['public_key'].split()) != 2):
        raise ValueError('Access filename and account details do not match.')
    if 'host_key_alias' in account and (not isinstance(account['host_key_alias'], str)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', account['host_key_alias'])):
        raise ValueError('Invalid pinned server name in the access ZIP.')
    if b'BEGIN OPENSSH PRIVATE KEY' not in data['ssh_key'] or not data['known_hosts'].strip():
        raise ValueError('Missing SSH key or pinned server identity.')
    return account, data


def verify_key(key, public_key):
    result = subprocess.run(['ssh-keygen', '-y', '-P', '', '-f', str(key)],
                            capture_output=True, text=True, timeout=10)
    if result.returncode or ' '.join(result.stdout.split()[:2]) != public_key:
        raise ValueError('The private key does not match this access package. Ask your instructor for help.')


def install(root, archive=None, home=None):
    root = setup.plain_path(Path(root).resolve())
    # Keep the private key outside the repository, with one immutable account
    # per workspace. Rebuilding/restarting the container can reimport the ZIP.
    identity = hashlib.sha256(str(root).encode()).hexdigest()[:16]
    home = Path(home).resolve() if home is not None else Path.home().resolve()
    parent = setup.plain_path(home / '.local/share/tensor-lab-4' / identity)
    destination = setup.plain_path(parent / 'access')
    if archive is None:
        candidates = list((root / '.uploads').glob('*.zip')) + list(root.glob('Lab_4_*_Access*.zip'))
        if len(candidates) > 1:
            raise ValueError('More than one access ZIP found. Keep only your own ZIP in .uploads.')
        archive = candidates[0] if candidates else None
    if archive is None:
        if destination.is_dir() and {p.name for p in destination.iterdir()} == ACCESS_FILES:
            for name in ACCESS_FILES:
                setup.plain_path(destination / name)
                if not (destination / name).is_file():
                    raise ValueError('Stored access is incomplete. Upload your original ZIP again.')
            return destination
        raise ValueError('Upload your emailed Lab_4_studentNN_Access.zip into .uploads, then run bash start_lab.sh.')
    account, data = read_archive(archive)
    parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if destination.exists():
        if not destination.is_dir() or {p.name for p in destination.iterdir()} != ACCESS_FILES:
            raise ValueError('Stored access is incomplete. Ask your instructor for help.')
        for name, body in data.items():
            target = setup.plain_path(destination / name)
            if not target.is_file() or target.read_bytes() != body:
                raise ValueError('This Codespace already has different access. Use your own original ZIP.')
        verify_key(destination / 'ssh_key', account['public_key'])
        return destination
    temporary = Path(tempfile.mkdtemp(prefix='import-', dir=parent))
    try:
        for name, body in data.items():
            with (temporary / name).open('xb') as stream:
                stream.write(body)
            (temporary / name).chmod(0o600)
        verify_key(temporary / 'ssh_key', account['public_key'])
        # Rename installs the complete validated set, preserving any old access.
        os.rename(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination
