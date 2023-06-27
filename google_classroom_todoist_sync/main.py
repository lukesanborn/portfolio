import time
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

import api_call


def main():
    now = datetime.datetime.now()
    start_program = time.time()
    api_call.driver()
    print(f"--- The program executed in {(time.time() - start_program)} at {now.strftime('%x %X')} ---")


if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(main)
    sched.add_job(main, "interval", minutes=3)
    sched.start()