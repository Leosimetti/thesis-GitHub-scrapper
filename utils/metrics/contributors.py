from github.StatsContributor import StatsContributor
from utils.metrics.base import BaseMetric, FakePaginatedList
from functools import reduce


class Contributors(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(lambda: FakePaginatedList(self._repo.get_stats_contributors()))
        self.total = self.main_container.totalCount

        self.metrics = {
            "[Contributors] Count": lambda: self._repo.get_contributors().totalCount,
        }
        self.calculate_metrics()

    def load(self, contributor: StatsContributor):
        author = contributor.author
        author.followers
        author.following
        author.public_repos
        author.team_count
        
        tmp = []
        for repo in author.get_repos():
            # print(f"got {repo.full_name}")
            repo.stargazers_count
            repo.subscribers_count
            repo.forks_count
            tmp.append(repo)
        
        contributor.repos = tmp
        return contributor

    def accumulate(self, contributor: StatsContributor):
        author = contributor.author
        repos = contributor.repos

        real_weeks = list(filter(lambda x: x.c > 0, contributor.weeks))
        additions, deletions = reduce(
            self._reducer, map(lambda w: (w.a, w.d), real_weeks))
        stars = sum(map(lambda x: x.stargazers_count, repos))
        watchers = sum(map(lambda x: x.subscribers_count, repos))
        forks = sum(map(lambda x: x.forks_count, repos))

        return {
            "commits": contributor.total,
            "weeks": len(real_weeks),
            "additions": additions,
            "deletions": deletions,
            "followers": author.followers or 0,
            "following": author.following or 0,
            "public_repos": author.public_repos or 0,
            "team_count": author.team_count or 0,
            "stars": stars or 0,
            "watchers": watchers or 0,
            "forks": forks or 0,
        }

    def get_final_metrics(self, *, commits, weeks, additions, deletions, followers, following, public_repos, team_count, stars, watchers, forks):
        return {
            "[Contributors Top-100] Average commits": commits/self.total,
            "[Contributors Top-100] Average participation weeks": weeks/self.total,
            "[Contributors Top-100] Average additions": additions/self.total,
            "[Contributors Top-100] Average deletions": deletions/self.total,
            "[Contributors Top-100] Average followers": followers/self.total,
            "[Contributors Top-100] Average following": following/self.total,
            "[Contributors Top-100] Average public repositories" : public_repos/self.total,
            "[Contributors Top-100] Average teams": team_count/self.total,
            "[Contributors Top-100] Average stars": stars/self.total,
            "[Contributors Top-100] Average watchers": watchers/self.total,
            "[Contributors Top-100] Average forks": forks/self.total,
        }