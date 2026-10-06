#!/usr/bin/env bash
set -euo pipefail
for tool in bash python3 ssh ssh-keygen scp chmod ls cat diff zip unzip tar; do
    command -v "$tool" >/dev/null || { printf 'Missing tool: %s\n' "$tool" >&2; exit 1; }
done
python3 -B -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
printf 'Lab 4 tools are ready. Upload your emailed access ZIP into .uploads, then run bash start_lab.sh.\n'
