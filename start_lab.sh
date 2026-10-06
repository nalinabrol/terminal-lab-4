#!/usr/bin/env bash
set -euo pipefail
lab4_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for lab4_command in bash python3 ssh ssh-keygen scp chmod ls cat diff zip unzip tar; do
    command -v "$lab4_command" >/dev/null || { printf 'Missing command: %s. Ask your instructor for setup help.\n' "$lab4_command" >&2; exit 1; }
done
python3 -B "$lab4_root/terminal-lab-4/student_start.py" "$@"
lab4_roll="$(cat "$lab4_root/.connection/current_roll")"
cd -- "$lab4_root/lab-work/lab4-$lab4_roll"
exec bash "$lab4_root/terminal-lab-4/terminal.sh"
