#!/usr/bin/env bash
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    python3 play.py
elif command -v python >/dev/null 2>&1; then
    python play.py
else
    echo "Python was not found on this computer."
    echo "Install it from https://python.org/downloads and try again."
    read -p "Press Enter to close..."
    exit 1
fi

read -p "Press Enter to close..."
