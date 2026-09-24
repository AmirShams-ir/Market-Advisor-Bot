#!/bin/bash
set -euo pipefail

APP_DIR="/home/amir/Market-Advisor-Bot"
SYSTEMD_DIR="/etc/systemd/system"

cp "$APP_DIR"/systemd/market-advisor-fetch@.service "$SYSTEMD_DIR/"
cp "$APP_DIR"/systemd/market-advisor-1h@.timer "$SYSTEMD_DIR/"
cp "$APP_DIR"/systemd/market-advisor-4h@.timer "$SYSTEMD_DIR/"
cp "$APP_DIR"/systemd/market-advisor-1day@.timer "$SYSTEMD_DIR/"
cp "$APP_DIR"/systemd/market-advisor-1week@.timer "$SYSTEMD_DIR/"

systemctl daemon-reload

echo "Installed Market Advisor Bot systemd units."
echo "Enable a symbol with:"
echo "  sudo systemctl enable --now market-advisor-1h@BTC_USD.timer"
echo "  sudo systemctl enable --now market-advisor-4h@BTC_USD.timer"
echo "  sudo systemctl enable --now market-advisor-1day@BTC_USD.timer"
echo "  sudo systemctl enable --now market-advisor-1week@BTC_USD.timer"
