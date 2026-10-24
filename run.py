from core.symbol_manager import setup_symbol


def main() -> None:
    print("=== Market Advisor Bot | Phase 1 ===")
    print("This command bootstraps historical candle data; recurring updates are managed by systemd.")

    config = setup_symbol()

    print()
    print(f"[DONE] Historical data collection finished for {config.symbol}.")
    print(f"[DB] data/{config.symbol.replace('/', '_')}.db")

    if config.auto_update:
        print()
        print("[INFO] Automatic updates were requested, but this interactive command does not enable systemd timers.")
        print("Install and enable the appropriate systemd timer units separately; see systemd/ and scripts/install-timers.sh.")


if __name__ == "__main__":
    main()
