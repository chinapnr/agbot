import subprocess
import sys
from datetime import datetime, timedelta
from time import sleep

import requests

worker_name = 'worker1'

def terminal_worker(wc: {}):
    p = wc.get('worker')
    if p is not None:
        p.terminate()


def recreate_worker(wc: {}):
    terminal_worker(wc)

    p = subprocess.Popen(['celery',
                          '-A',
                          'agbot.core.task.task_exec_celery',
                          'worker',
                          '--loglevel=info',
                          '--pool=eventlet',
                          '-E',
                          '-Qagbot-dev.celery.tasks',
                          '-c50',
                          '-n%h.{}'.format(worker_name)
                          ], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    wc['worker'] = p
    wc['boot_time'] = datetime.now()


if __name__ == '__main__':
    wc = {}
    recreate_worker(wc)
    while True:
        try:
            sleep(30)
            if datetime.now() - wc['boot_time'] > timedelta(hours=1):
                recreate_worker(wc)
                continue
            # get monitor data from flower
            worker_list = requests.get('http://localhost:5555/dashboard?json=1', timeout=5).json().get('data')
            for worker in worker_list:
                if worker.get('hostname').endswith(worker_name):
                    if not worker.get('status'):
                        recreate_worker(wc)
        except KeyboardInterrupt as e:
            terminal_worker(wc)
            raise e
        except BaseException as e:
            print(e)
            terminal_worker(wc)
