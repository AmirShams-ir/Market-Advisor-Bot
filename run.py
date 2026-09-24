from core.database import create_tables
from core.scheduler import run_scheduled
from core.symbol_manager import setup_symbol


def main() -> None:
    print("=== Market Advisor Bot | Phase 1 ===")

    create_tables()
    config = setup_symbol()

    run_scheduled([config])


if __name__ == "__main__":
    main()
