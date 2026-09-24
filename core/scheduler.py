import schedule
import time

from core.fetcher import update_all

def run():

    update_all()

    schedule.every(1).minutes.do(update_all)

    while True:

        schedule.run_pending()

        time.sleep(1)