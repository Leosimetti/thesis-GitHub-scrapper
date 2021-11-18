from datetime import datetime
import time
import csv
from pprint import pprint

import repos

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
    Stars,
    Forks,
    Releases,
    Meta,
    Pulls,
    Commits,
    Issues,
    WorkflowRuns,
    # Contributors,
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
            metric_ctx.submit(metric, repo)

if __name__ == "__main__":
    now = time.perf_counter()
    TO_CALC = repos.NEW_REPOS
    

    # with ThreadPoolExecutor(max_workers=5) as p:
    #     for repo in TO_CALC:
    #         p.submit(calc_metrics, repo)

    for repo in TO_CALC:
        calc_metrics(repo)

    print(f'Took {time.perf_counter() - now} s')

