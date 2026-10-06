#!/usr/bin/env bash
set -euo pipefail
lab4_kit="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export LAB4_SSH_CONFIG="${LAB4_SSH_CONFIG:-$lab4_kit/../.connection/ssh_config}"
export BASH_SILENCE_DEPRECATION_WARNING=1
export LAB4_CHECKER="$lab4_kit/check.py"
if [[ ! -f "$LAB4_SSH_CONFIG" ]]; then
    printf 'Configure your private SSH connection first. See lab-4/README.md.\n' >&2
    exit 1
fi
printf 'Lab 4 terminal. ssh and scp use your private lab connection; check_lab checks your work.\n'
printf 'Use exit to leave this starting terminal when finished.\n'
exec bash --noprofile --rcfile "$lab4_kit/terminal.rc" -i
