#!/usr/bin/env bash
set -euo pipefail
lab4_kit="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for lab4_command in bash python3 ssh scp chmod ls cat diff zip unzip tar; do
    command -v "$lab4_command" >/dev/null || { printf 'Missing command: %s\n' "$lab4_command" >&2; exit 1; }
done
python3 -B "$lab4_kit/setup.py" "$@"
