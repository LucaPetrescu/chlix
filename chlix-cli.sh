#!/bin/bash

# Lightweight runtime launcher for the chlix CLI

# Resolve the actual script location even when called via symlink (e.g. ~/.local/bin/chlix)
SCRIPT_SOURCE="${BASH_SOURCE[0]}"
while [ -L "${SCRIPT_SOURCE}" ]; do
    SCRIPT_DIR="$( cd -P "$( dirname "${SCRIPT_SOURCE}" )" && pwd )"
    SCRIPT_SOURCE="$(readlink "${SCRIPT_SOURCE}")"
    [[ "${SCRIPT_SOURCE}" != /* ]] && SCRIPT_SOURCE="${SCRIPT_DIR}/${SCRIPT_SOURCE}"
done
SCRIPT_DIR="$( cd -P "$( dirname "${SCRIPT_SOURCE}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "${SCRIPT_DIR}/.venv" ]; then
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/.venv/bin/activate"
elif [ -d "${SCRIPT_DIR}/venv" ]; then
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/venv/bin/activate"
fi

python3 "${SCRIPT_DIR}/main.py" "$@"

