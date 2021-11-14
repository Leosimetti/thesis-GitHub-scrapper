from datetime import datetime
from time import time
from github.Issue import Issue
from collections import Counter
from utils.metrics.base import BaseMetric
from concurrent.futures import ThreadPoolExecutor


class Issues(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)

        def is_bug(label):
            in_desc = "bug" in label.description.lower() if label.description else False
            in_title = "bug" in label.name.lower() if label.name else False
            return in_title or in_desc

        self.main_container = self.get_main_container(lambda: self._repo.get_issues(state="all"))
        self.total = self.main_container.totalCount - self._repo.get_pulls(state="all").totalCount
        
        if self.total > 0:
            labels = self._repo.get_labels()
            self.bug_labels = [label.name for label in labels if is_bug(label)]

            self.metrics = {
                "[Issues] Total comments": lambda: self._repo.get_issues_comments().totalCount,
                "[Issues] Count": lambda: self.total,
                "[Issues] Open": lambda: self._repo.open_issues_count,
                "[Issues] Labels": lambda: self._repo.get_labels().totalCount,
            }
        else:
            self.total = 0
            self.metrics = {
               "[Issues] Count": lambda: self.total,
            }

        self.calculate_metrics()

    def _get_closed_issues_to_total_issues(self):
        total = self._repo.get_issues(state="all").totalCount
        if total == 0:
            return 0

        closed = self._repo.get_issues(state="closed").totalCount
        return closed/total

    def accumulate(self, issue: Issue):
        if issue.pull_request:
            return {
                "participants":0,
                "comments":0,
                "labels":0,
                "close_time":0,
                "assignees":0,
                "title_len":0,
                "body_len":0,
                "closed": 0,
                "bugs":0,
                "dates":[],
                "total_comments_len":0,
                "total_comments_interval_days":0,
                "reactions":0,
            }
        else:
            return self._accumulate(issue)

    def _accumulate(self, issue: Issue):
        assignees = len(issue.assignees)
        body_len = len(issue.body) if issue.body else 0
        title_len = len(issue.title)
        labels = len(issue.labels)
        bugs = int(any(label.name in self.bug_labels for label in issue.labels))
        total_comments_len = sum(len(comment.body)
                                 for comment in issue.comments_list)

        if issue.state == "closed" and issue.closed_at is not None:
            close_time = (issue.closed_at - issue.created_at).days
        else:
            close_time = 0

        has_comments = len(issue.comments_list) > 0
        if has_comments:
            shifted_comment_list = [
                issue.comments_list[0]] + issue.comments_list
            comment_intervals = sum(
                (nxt.created_at.date() - current.created_at.date()).total_seconds()
                for nxt, current in zip(issue.comments_list, shifted_comment_list)
            )/60/60/24

        return {
            "participants": issue.participants,
            "comments": issue.comments,
            "labels": labels,
            "close_time": close_time,
            "closed" : 1 if issue.state == "closed" else 0,
            "assignees": assignees,
            "title_len": title_len,
            "body_len": body_len,
            "bugs": bugs,
            "dates": [issue.created_at.date()],
            "reactions": issue.reactions,
            "total_comments_len": total_comments_len,
            "total_comments_interval_days": comment_intervals if has_comments else 0,
        }

    def load(self, issue: Issue):
        if issue.pull_request:
            return issue
        else:
            return self._load(issue)

    def _load(self, issue):
        issue.user
        issue.comments
        issue.labels
        issue.closed_at
        issue.created_at
        issue.assignees
        issue.body
        issue.title
        issue.state
        issue.pull_request
        issue.closed_by

        if not hasattr(issue, "participants"):
            comments = issue.get_comments()
            reactions = sum(comment.get_reactions(
            ).totalCount for comment in comments)
            participants = set(
                map(lambda comment: comment.user.id, comments))

            issue.participants = len(
                Counter(participants - {issue.user.id}))
            issue.comments_list = list(comments)
            issue.reactions = reactions + issue.get_reactions().totalCount

        return issue

    def get_final_metrics(self, *, closed, dates, participants, comments, labels, assignees, close_time, title_len, body_len, bugs, total_comments_len, total_comments_interval_days, reactions):
        date_counts = Counter(dates).values()
        unique_issue_dates = len(date_counts)
        max_issues = max(date_counts)
        age_days = (datetime.now() - self._repo.created_at).days

        delattr(self, "bug_labels")

        return {
            "[Issues] Average participants (beside creator)": participants/self.total,
            "[Issues] Average assignees": assignees/self.total,
            "[Issues] Average labels": labels/self.total,
            "[Issues] Average reactions": reactions/comments if comments else None,
            "[Issues] Average closing time (days)": close_time/closed if closed else None,
            "[Issues] Average comment interval (days)": total_comments_interval_days/comments if comments else None,
            "[Issues] Average comments": comments/self.total,
            "[Issues] Average comment len (chars)": total_comments_len/comments if comments else None,
            "[Issues] Average title len (chars)": title_len/self.total,
            "[Issues] Average body len (chars)": body_len/self.total,
            "[Issues] Per day": self.total/unique_issue_dates,
            "[Issues] Per day (True)": self.total/age_days,
            "[Issues] Maximum per day": max_issues,
            "[Issues] Closed to total": closed/self.total,
            "[Issues] Bugs to total": bugs/self.total,
            # "issues_minimum_per_day": min_issues,
        }
