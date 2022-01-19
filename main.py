from datetime import datetime
import time
import csv
from pprint import pprint

import repos

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import reduce
import sys
import traceback
import random
import glob
import pickle
from collections import defaultdict

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
    Pulls,
    Commits,
    Issues,
    WorkflowRuns,
    Meta,
    Contributors,
]

def handle_exception(errorClass, exc, trace):
    with open("aboba.txt", "a") as f:
        trace_str = "".join(traceback.format_tb(trace))
        header = f'[{datetime.now()}] {errorClass}: {exc} \n'
        f.write( header  + trace_str + "\n")
        sys.__excepthook__(errorClass, exc, trace)

sys.excepthook = handle_exception


def find_missing_metrics():
    missing_ones = defaultdict(lambda: METRICS.copy())
    for p in glob.glob(".\intermediate\*\*.pickle"):
        with open(p, "rb") as file:
            metric = pickle.load(file)
            dic = metric.__dict__
            repo_name = dic.pop("repo_name")
            metric_type = p.split('\\')[-1].split(".")[0]

            # print(f"{metric_type} {list(map(lambda x: x.__name__,metrics))}")
            missing_ones[repo_name] = [x for x in missing_ones[repo_name] if x.__name__ != metric_type]

    return missing_ones

def calculate_missing_metrics():
    missing_ones = find_missing_metrics()
    print(f"{sum(map(len, missing_ones.values()))} metrics missing")

    tmp = list(missing_ones.items())
    random.shuffle(tmp)

    for repo_name, metric_types in tmp:
        random.shuffle(metric_types)
        for metric in metric_types:
            try:
                metric(repo_name)
            except Exception as e:
                print(f"[{repo_name}] Failed {metric.__name__} with {e}")
                continue

def calculate_metrics(array, retry=True, threaded=False):
    def calc_metrics(repo):
        for metric in METRICS:
            metric(repo)
    def main():
        random.shuffle(array)
        random.shuffle(METRICS)
        try:
            for repo in array:
                calc_metrics(repo)
        except:
            main()
    
    if retry:
        main()
    else:
        if threaded:
            with ThreadPoolExecutor(max_workers=2) as p:
                for repo in array:
                    p.submit(calc_metrics, repo)
        else:
            for repo in array:
                calc_metrics(repo)

if __name__ == "__main__":
    
    now = time.perf_counter()

    TO_CALC = repos.NEW_REPOS
    # calculate_metrics(TO_CALC)
    # METRICS[0](TO_CALC[0])
    
    calculate_missing_metrics()

    print(f'Took {time.perf_counter() - now} s')

