#!/bin/bash

for VAR_NAME in DEFAULT_REPO_NAME FLATPACK_NAME SCRIPT_DIR; do
  if [[ -z "${!VAR_NAME}" ]]; then
    echo "Error: $VAR_NAME is not set. Please set the $VAR_NAME environment variable." >&2
    exit 1
  fi
done

CURRENT_DIR="$(pwd)"
OS=$(uname)

WORK_DIR="$CURRENT_DIR/$FLATPACK_NAME/build/$DEFAULT_REPO_NAME"

if [[ -d "/content" ]]; then
  if command -v nvidia-smi &> /dev/null; then
    echo "🌀 Detected Colab GPU environment"
    DEVICE="cuda"
  else
    echo "🌀 Detected Colab CPU environment"
    DEVICE="cpu"
  fi
  export VENV_PYTHON="${SCRIPT_DIR}/bin/python"
elif [ "$OS" = "Darwin" ]; then
  echo "🍎 Detected macOS environment"
  export VENV_PYTHON="${SCRIPT_DIR}/bin/python"
  DEVICE="mps"
elif [ "$OS" = "Linux" ]; then
  if [[ -x "$(command -v python3)" ]]; then
    export VENV_PYTHON="python3"
  else
    export VENV_PYTHON="python"
  fi
  echo "🐧 Detected Linux environment"
  DEVICE="cpu"
else
  echo "❓ Detected other OS environment"
  DEVICE="cpu"
fi

export VENV_PIP="$(dirname $VENV_PYTHON)/pip"

echo "Determined WORK_DIR: $WORK_DIR"
echo "Determined DEVICE: $DEVICE"

if [[ -d "$WORK_DIR" ]]; then
  cd "$WORK_DIR"
  echo "Changed to directory $WORK_DIR"
else
  echo "Error: Failed to change to directory $WORK_DIR" >&2
  exit 1
fi