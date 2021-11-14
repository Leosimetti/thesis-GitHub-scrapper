from datetime import datetime, timedelta
# import re
from github import Github, Issue, PaginatedList
# from github.Requester import Requester
# import pickle
# import asyncio
# from tqdm import tqdm
# from main import IteratorLoopWrapper, TOKENS
import csv
from utils.settings import TOKENS
from pprint import pprint as print
import sys



if __name__ == "__main__":

    repo = Github(TOKENS[5]).get_repo("gokcehan/lf")

    def recursive_helper(file):
        if file.type == "dir":
            return 1 + sum(map(recursive_helper,repo.get_contents(file.path)))
        else: 
            return 0 

    # hooks = repo.get_milestones()
    all_files = repo.get_contents("/")
    results = sum(map(recursive_helper, all_files))

    print(results)

    # githubs = list(map(Github, TOKENS ))
    # for g in githubs:
    #     limit = g.get_rate_limit().core
    #     print(f"Left: {limit.remaining} Reset at: {limit.reset + timedelta(hours=3)}")

    