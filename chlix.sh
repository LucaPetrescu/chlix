#!/bin/bash

# Installer/bootstrap script for chlix.
# Run this once from the repo to set up the venv and global `chlix` command.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Setting up chlix in ${SCRIPT_DIR}..."

# Create or reuse virtual environment
if [ -d "${SCRIPT_DIR}/.venv" ]; then
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/.venv/bin/activate"
elif [ -d "${SCRIPT_DIR}/venv" ]; then
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/venv/bin/activate"
else
    python3 -m venv "${SCRIPT_DIR}/.venv" --prompt=chlix
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/.venv/bin/activate"
fi

echo "Installing Python dependencies..."
pip install -r "${SCRIPT_DIR}/requirements.txt"

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
