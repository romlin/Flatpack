#!/bin/bash

# "${VENV_PIP}"
# "${VENV_PYTHON}"

init_script="$SCRIPT_DIR/init.sh"
[ -f "$init_script" ] || { echo "init.sh not found, exiting."; exit 1; }
source "$init_script" || { echo "Failed to load init.sh."; exit 1; }

"${VENV_PIP}" install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu

cd ..

# "${VENV_PYTHON}" capture.py --mode screenshot
# "${VENV_PYTHON}" capture.py --mode webcam
"${VENV_PYTHON}" capture.py --mode youtube --url https://www.youtube.com/watch?v=dQw4w9WgXcQ