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
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
VENV_DIR="${PROJECT_ROOT}/.venv"

# Activate virtual environment if it exists
if [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1090
    source "${VENV_DIR}/bin/activate"
fi

python3 "${PROJECT_ROOT}/main.py" "$@"

