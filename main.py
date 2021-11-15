from datetime import datetime
import time
import csv
from pprint import pprint

from  utils import settings

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import reduce
import sys
import traceback

from utils.metrics.contributors import Contributors
from utils.metrics.workflowRuns import WorkflowRuns
from utils.metrics.releases import Releases
from utils.metrics.commits import Commits
from utils.metrics.issues import Issues
from utils.metrics.pulls import Pulls
from utils.metrics.stars import Stars
from utils.metrics.forks import Forks
from utils.metrics.meta import Meta

METRICS = [
    Meta,
    # Contributors,
    # Stars,
    # Releases,
    # Forks,
    # Pulls,
    # Commits,
    # Issues,
    # WorkflowRuns,
]

def handle_exception(errorClass, exc, trace):
    with open("aboba.txt", "a") as f:
        trace_str = "".join(traceback.format_tb(trace))
        header = f'[{datetime.now()}] {errorClass}: {exc} \n'
        f.write( header  + trace_str + "\n")
        sys.__excepthook__(errorClass, exc, trace)

sys.excepthook = handle_exception

def calc_metrics(repo):
    with (ThreadPoolExecutor(max_workers=1) as metric_ctx):
        for metric in METRICS:
            # metric(repo)
            metric_ctx.submit(metric, repo)

if __name__ == "__main__":

    TO_CALC = settings.CALCULATED_REPOS

    now = time.time()
    # res = METRICS[0](TO_CALC[0])
    
    with ThreadPoolExecutor(max_workers=5) as p:
        for repo in TO_CALC:
            p.submit(calc_metrics, repo)

    # for repo in TO_CALC:
    #     calc_metrics(repo)

    print(f'Took {time.time() - now} s')

