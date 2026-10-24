#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"

if [[ "$(id -u)" -eq 0 ]]; then
  echo "Please run this script as your normal user (e.g. amir), not with sudo."
  echo "The script will use sudo only for installing Debian packages."
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "ERROR: sudo is required to install Debian system packages."
  exit 1
fi

echo "[1/4] Installing Debian prerequisites..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip ca-certificates

echo "[2/4] Creating virtual environment..."
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[3/4] Installing/updating Python dependencies..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

echo "[4/4] Checking imports..."
"$VENV_DIR/bin/python" - <<'PY'
import pandas
import sqlalchemy
import dotenv
import twelvedata
print("Python dependencies: OK")
print("pandas:", pandas.__version__)
print("SQLAlchemy:", sqlalchemy.__version__)
PY

mkdir -p "$APP_DIR/data" "$APP_DIR/logs"
touch "$APP_DIR/data/.gitkeep" "$APP_DIR/logs/.gitkeep"

echo
echo "Installation completed."
echo "Activate manually with: source .venv/bin/activate"
echo "Run the CLI with: .venv/bin/python run.py"
echo "Do not run the application with sudo."
