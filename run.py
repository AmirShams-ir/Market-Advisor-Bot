from core.database import create_symbol_tables
from core.scheduler import run_scheduled
from core.symbol_manager import setup_symbol


def main() -> None:
    print("=== Market Advisor Bot | Phase 1 ===")

    config = setup_symbol()
    create_symbol_tables(config.symbol)

    run_scheduled([config])


if __name__ == "__main__":
    main()
