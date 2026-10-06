#!/usr/bin/env python3
"""Write a private, kit-local SSH profile using an existing verified host-key file."""
import argparse
import os
from pathlib import Path
import re
import sys


def quoted_path(value):
    value = value.as_posix() if isinstance(value, Path) else str(value)
    if any(c in value for c in '\n\r\x00%'):
        raise ValueError('Unsupported character in SSH file path')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def configure(host, user, key, known_hosts, destination, port=22, host_key_alias=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', host):
        raise ValueError('Use a hostname or IPv4 address')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', user) or not 1 <= port <= 65535:
        raise ValueError('Invalid username or port')
    if host_key_alias and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*',host_key_alias):
        raise ValueError('Invalid pinned host-key name')
    key, known_hosts = Path(key).resolve(), Path(known_hosts).resolve()
    if not key.is_file() or not known_hosts.is_file() or not known_hosts.read_text(encoding='utf-8').strip():
        raise ValueError('Provide an existing private key and instructor-verified known_hosts file')
    if os.name == 'posix' and key.stat().st_mode & 0o077:
        raise ValueError('The private key must have no group/others access; use chmod 600 on your own key')
    destination = Path(destination).absolute()
    if destination.is_symlink() or destination.parent.is_symlink():
        raise ValueError('Connection path must not be a symbolic link')
    text = (f'Host lab-server\n  HostName {host}\n  User {user}\n  Port {port}\n'
            f'  IdentityFile {quoted_path(key)}\n  UserKnownHostsFile {quoted_path(known_hosts)}\n'
            '  IdentitiesOnly yes\n  StrictHostKeyChecking yes\n  ConnectTimeout 12\n'
            '  ServerAliveInterval 15\n  ServerAliveCountMax 2\n'
            '  ForwardAgent no\n  ClearAllForwardings yes\n  ControlMaster no\n')
    if host_key_alias:
        text += '  HostKeyAlias '+host_key_alias+'\n'
    if destination.exists():
        if destination.read_text(encoding='utf-8') != text:
            raise ValueError('An existing connection differs. Preserve it and choose a new config path.')
        return False
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as output:
        output.write(text)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--known-hosts', type=Path, required=True)
    parser.add_argument('--port', type=int, default=22)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent.parent / '.connection/ssh_config')
    args = parser.parse_args()
    try:
        created = configure(args.host, args.user, args.key, args.known_hosts, args.output, args.port)
    except (OSError, ValueError) as error:
        sys.exit(str(error))
    print('Created private connection profile.' if created else 'Matching connection profile preserved.')


if __name__ == '__main__':
    main()
