# systemd deployment

Install the units on the dedicated Debian host:

```bash
cd /home/amir/Market-Advisor-Bot
sudo bash scripts/install-timers.sh
```

The fetch service runs as user `amir` and exits after one fetch.

The timers are independent from any SSH/terminal session.

Enable the desired symbol/timeframe timers:

```bash
sudo systemctl enable --now market-advisor-1h@BTC_USD.timer
sudo systemctl enable --now market-advisor-4h@BTC_USD.timer
sudo systemctl enable --now market-advisor-1day@BTC_USD.timer
sudo systemctl enable --now market-advisor-1week@BTC_USD.timer
```

Check timers:

```bash
systemctl list-timers 'market-advisor-*'
```

Check logs:

```bash
journalctl -u market-advisor-fetch@BTC_USD-1h.service
```

The database is stored at `data/BTC_USD.db`.
