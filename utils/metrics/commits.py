from datetime import datetime
from typing import Counter
from github import Commit, CommitStats

from utils.metrics.base import BaseMetric


class Commits(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(self._repo.get_commits)
        self.total = self.main_container.totalCount

        first_commit = self.main_container.reversed[0]
        last_commit = self.main_container[0]

        self.metrics = {
            "[Commits] Count": lambda: self.total,
            # "commits_per_day": self._get_average_commits_per_day,
            # "commits_age_days": self._get_commit_age,
            "[Commits] Days since first": lambda: 
                (datetime.now() - first_commit.commit.author.date).days,
            "[Commits] Days since last": lambda: 
                (datetime.now() - last_commit.commit.author.date).days,
        }

        self.calculate_metrics()

    def accumulate(self, commit: Commit):
        stats: CommitStats = commit.stats

        files = len(commit.files) if commit.files else 1
        real_commit = commit.commit
        date = (real_commit.author.date).date()
        msg_len = len(real_commit.message)

        return {
            "additions": stats.additions,
            "deletions": stats.deletions,
            "dates": [date],
            "msg_len": msg_len,
            "files": files
        }

    def load(self, commit):
        commit.stats
        commit.files
        commit.commit

        return commit

    def get_final_metrics(self, *, additions, deletions, dates, files, msg_len):
        date_values = Counter(dates).values()
        unique_commit_dates = len(date_values)
        files_without_first_commit = files - \
            len(self.main_container.reversed[0].files)
        max_commints = max(date_values)
        age_days = (datetime.now() - self._repo.created_at).days


        return {
            "[Commits] Total lines added": additions,
            "[Commits] Total lines deleted": deletions,
            "[Commits] Average additions": additions/self.total,
            "[Commits] Average deletions": deletions/self.total,
            "[Commits] Average files changed": files_without_first_commit/self.total,
            "[Commits] Average message length (chars)": msg_len/self.total,
            "[Commits] Per day": self.total/unique_commit_dates,
            "[Commits] Per day (True)": self.total/age_days,
            "[Commits] Maximum per day": max_commints,
        }
