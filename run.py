from core.database import create_tables
from core.scheduler import run

create_tables()

run()