#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
ENV_FILE="$APP_DIR/.env"
GITIGNORE_FILE="$APP_DIR/.gitignore"

if [[ "$(id -u)" -eq 0 ]]; then
  echo "Please run this script as your normal user (e.g. amir), not with sudo."
  echo "The script will use sudo only for installing Debian packages."
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "ERROR: sudo is required to install Debian system packages."
  exit 1
fi

echo "[1/5] Installing Debian prerequisites..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip ca-certificates

echo "[2/5] Creating virtual environment..."
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[3/5] Installing/updating Python dependencies..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

echo "[4/5] Checking imports..."
"$VENV_DIR/bin/python" - <<'PY'
import pandas
import sqlalchemy
import dotenv
import twelvedata

print("Python dependencies: OK")
print("pandas:", pandas.__version__)
print("SQLAlchemy:", sqlalchemy.__version__)
PY

echo "[5/5] Configuring Twelve Data API key..."

# Ensure the environment file is never tracked by Git.
if [[ ! -f "$GITIGNORE_FILE" ]]; then
  touch "$GITIGNORE_FILE"
fi
if ! grep -qxF '.env' "$GITIGNORE_FILE"; then
  printf '\n# Local secrets\n.env\n' >> "$GITIGNORE_FILE"
fi

# Read an existing key, if present, without displaying it.
EXISTING_KEY=""
if [[ -f "$ENV_FILE" ]]; then
  EXISTING_KEY="$(sed -n 's/^TWELVE_API_KEY=//p' "$ENV_FILE" | tail -n 1)"
fi

if [[ -n "$EXISTING_KEY" ]]; then
  read -r -p "A Twelve Data API key is already configured. Replace it? [y/N]: " REPLACE_KEY
  if [[ "${REPLACE_KEY,,}" == "y" || "${REPLACE_KEY,,}" == "yes" ]]; then
    read -r -s -p "Enter your Twelve Data API key: " API_KEY
    printf '\n'
  else
    API_KEY="$EXISTING_KEY"
    echo "Keeping the existing API key."
  fi
else
  while [[ -z "${API_KEY:-}" ]]; do
    read -r -s -p "Enter your Twelve Data API key: " API_KEY
    printf '\n'
    if [[ -z "$API_KEY" ]]; then
      echo "The API key cannot be empty. Please try again."
    fi
  done
fi

if [[ -z "${API_KEY:-}" ]]; then
  echo "ERROR: No API key was provided. .env was not updated." >&2
  exit 1
fi

# Write atomically with restrictive permissions. Avoid shell tracing of secrets.
umask 077
TMP_ENV="$(mktemp "$APP_DIR/.env.tmp.XXXXXX")"
trap 'rm -f "${TMP_ENV:-}"' EXIT
if [[ -f "$ENV_FILE" ]]; then
  # Preserve unrelated variables while replacing TWELVE_API_KEY.
  awk '!/^TWELVE_API_KEY=/' "$ENV_FILE" > "$TMP_ENV"
fi
printf 'TWELVE_API_KEY=%s\n' "$API_KEY" >> "$TMP_ENV"
chmod 600 "$TMP_ENV"
mv -f "$TMP_ENV" "$ENV_FILE"
chmod 600 "$ENV_FILE"
unset API_KEY EXISTING_KEY

mkdir -p "$APP_DIR/data" "$APP_DIR/logs"
touch "$APP_DIR/data/.gitkeep" "$APP_DIR/logs/.gitkeep"

echo
echo "Installation and configuration completed."
echo "API key saved to .env with permissions 600."
echo "Verify configuration (does not print the key):"
echo "  .venv/bin/python -c 'from config import API_KEY; print(\"API key loaded:\", bool(API_KEY))'"
echo "Run the CLI with: .venv/bin/python run.py"
echo "Do not run the application with sudo."
