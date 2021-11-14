from collections import Counter
from datetime import datetime
from github.PullRequest import PullRequest
from utils.metrics.base import BaseMetric
from tqdm import tqdm


class Pulls(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)

        self.main_container = self.get_main_container(
            lambda: self._repo.get_pulls(state="all"))
        self.total = self.main_container.totalCount

        self.metrics = {
            "[Pulls] Count": lambda: self.total,
            "[Pulls] Closed to total": self._get_closed_pulls_to_total,
        }
        self.calculate_metrics()

    def _get_closed_pulls_to_total(self):
        ttl_pulls = self._repo.get_pulls(state="all").totalCount
        closed_pulls = self._repo.get_pulls(state="closed").totalCount

        if ttl_pulls:
            return closed_pulls/ttl_pulls
        else:
            return 0

    def load(self, pull: PullRequest):
        pull.closed_at
        pull.created_at
        pull.state
        pull.commits
        pull.comments
        pull.additions
        pull.assignees
        pull.deletions
        pull.body
        pull.changed_files
        pull.draft
        pull.labels
        pull.mergeable
        pull.merged
        pull.user
        pull.title
        pull.review_comments
        pull.review_requests = list(pull.get_review_requests()[0])

        return pull

    def accumulate(self, pull: PullRequest):
        days = (pull.closed_at -
                pull.created_at).days if pull.state == "closed" else 0
        mergeable = pull.mergeable if pull.mergeable is not None else 0
        reviewers = len(pull.review_requests)
        assignees = len(pull.assignees)
        body = len(pull.body) if pull.body else 0
        title = len(pull.title) if pull.title else 0
        labels = len(pull.labels)
        # Todo used labels/total labels?

        return {
            "days": days,
            "body": body,
            "title": title,
            "reviewers": reviewers,
            "assignees": assignees,
            "commits": pull.commits,
            "comments": pull.comments,
            "additions": pull.additions,
            "deletions": pull.deletions,
            "files": pull.changed_files,
            "labels": labels,
            "mergeables": mergeable,
            "mergedes": pull.merged,
            "dates": [pull.created_at.date()],
            "review_comments": pull.review_comments,
        }

    def get_final_metrics(self, *, dates, review_comments, mergedes, mergeables, labels, files, assignees, body, title, additions, deletions, days, reviewers, comments, commits):
        closed_pulls = self._repo.get_pulls(state="closed").totalCount
        date_counts = Counter(dates).values()
        unique_pull_dates = len(date_counts)
        # min_pull = min(date_counts)
        max_pull = max(date_counts)
        age_days = (datetime.now() - self._repo.created_at).days

        return {
            "[Pulls] Total lines added": additions,
            "[Pulls] Total lines deleted": deletions,
            "[Pulls] Average lines deleted": deletions/self.total,
            "[Pulls] Average lines added": additions/self.total,
            "[Pulls] Average closing time (days)": days/closed_pulls if closed_pulls else None,
            "[Pulls] Average reviewers": reviewers/self.total,
            "[Pulls] Average comments": comments/self.total,
            "[Pulls] Average review comments": review_comments/self.total,
            "[Pulls] Average commits": commits/self.total,
            "[Pulls] Average assignees": assignees/self.total,
            "[Pulls] Average body len (chars)": body/self.total,
            "[Pulls] Average title len (chars)": title/self.total,
            "[Pulls] Average files changed": files/self.total,
            "[Pulls] Average labels": labels/self.total,
            "[Pulls] Mergeable to total": mergeables/self.total,
            "[Pulls] Merged to total": mergedes/self.total,
            "[Pulls] Created per day": self.total/unique_pull_dates,
            "[Pulls] Created per day (True)": self.total/age_days,
            "[Pulls] Maximum created per day": max_pull,
            # "pulls_minimum_per_day": min_pull,
        }
