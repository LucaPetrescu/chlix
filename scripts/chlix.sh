#!/bin/bash

# Installer/bootstrap script for chlix.
# Run this once from the repo to set up the venv and global `chlix` command.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo "Setting up chlix in ${PROJECT_ROOT}..."

# Create or reuse virtual environment
if [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1090
    source "${VENV_DIR}/bin/activate"
else
    python3 -m venv "${VENV_DIR}" --prompt=chlix
    # shellcheck disable=SC1090
    source "${VENV_DIR}/bin/activate"
fi

echo "Installing Python dependencies..."
python3 -m pip install -r "${PROJECT_ROOT}/requirements.txt"

# Ensure ~/.local/bin exists and create/refresh a symlink for global usage
LOCAL_BIN="${HOME}/.local/bin"
mkdir -p "${LOCAL_BIN}"

ln -sf "${SCRIPT_DIR}/chlix-cli.sh" "${LOCAL_BIN}/chlix"
chmod +x "${SCRIPT_DIR}/chlix-cli.sh"

# Ensure ~/.local/bin is on the PATH, adding it to the user's shell config if needed
case ":$PATH:" in
    *":${LOCAL_BIN}:"*)
        echo "~/.local/bin is already on your PATH."
        ;;
    *)
        SHELL_NAME="$(basename "${SHELL:-bash}")"
        case "${SHELL_NAME}" in
            bash)
                CONFIG_FILE="${HOME}/.bashrc"
                ;;
            zsh)
                CONFIG_FILE="${HOME}/.zshrc"
                ;;
            fish)
                CONFIG_FILE="${HOME}/.config/fish/config.fish"
                ;;
            *)
                CONFIG_FILE="${HOME}/.profile"
                ;;
        esac

        mkdir -p "$(dirname "${CONFIG_FILE}")"

        if [ "${SHELL_NAME}" = "fish" ]; then
            {
                echo ""
                echo "# Added by chlix to include ~/.local/bin in PATH"
                echo "set -Ux PATH \"${LOCAL_BIN}\" \$PATH"
            } >> "${CONFIG_FILE}"
        else
            {
                echo ""
                echo "# Added by chlix to include ~/.local/bin in PATH"
                echo "export PATH=\"${LOCAL_BIN}:\$PATH\""
            } >> "${CONFIG_FILE}"
        fi

        echo "Added ${LOCAL_BIN} to PATH in ${CONFIG_FILE}."
        echo "Open a new shell or run: source \"${CONFIG_FILE}\""
        ;;
esac

./run-chromadb.sh

echo
echo "✅ chlix installed."
echo "You can now run the CLI as:"
echo "  chlix list"
echo "  chlix index /path/to/repo"
echo "  chlix search <collection> \"your query\""
