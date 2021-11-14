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

    now = time.time()
    # res = METRICS[0](settings.REPOS[0])
    
    # with ThreadPoolExecutor(max_workers=25) as p:
    #     for repo in settings.REPOS:
    #         p.submit(calc_metrics, repo)

    for repo in settings.REPOS:
        calc_metrics(repo)


    # repos = list(map(lambda x: reduce(lambda acc, el: el.__dict__ | acc  ,x, {}), dicts)) 

    # with open('results.pickle', 'rb') as handle:
    #     old_data = pickle.load(handle)
    #     new_data = repos + old_data
    # with open('results.pickle', 'wb') as handle:
    #     pickle.dump(new_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # pprint(new_data)

    # with open('results.csv', 'a', newline='') as csvfile:
    #     field_names = {field for repo in repos for field in repo.keys()}
    #     field_names = list(field_names)
    #     field_names.remove("name")
    #     field_names.insert(0, "name")
    #     field_names.insert(1, "date")
        
    #     writer = csv.DictWriter(csvfile, fieldnames=field_names)
    #     # writer.writeheader()
        
    #     current_date = datetime.now().date()
    #     repos = list(map(lambda r:r | {"date": current_date}, repos))
    #     writer.writerows(repos)

    print(f'Took {time.time() - now} s')

