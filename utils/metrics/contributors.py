from github.StatsContributor import StatsContributor
from utils.metrics.base import BaseMetric
from functools import reduce



class Contributors(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(self._repo.get_stats_contributors)
        self.total = len(self.main_container)

        self.metrics = {
            "[Contributors] Count": lambda: self._repo.get_contributors().totalCount,
        }
        self.calculate_metrics()

    def accumulate(self, contributor: StatsContributor):
        commits = contributor.total
        real_weeks = list(filter(lambda x: x.c > 0, contributor.weeks))
        additions, deletions = reduce(
            self._reducer, map(lambda w: (w.a, w.d), real_weeks))

        return {"commits": commits,
                "weeks": len(real_weeks),
                "additions": additions,
                "deletions": deletions
                }

    def get_final_metrics(self, *, commits, weeks, additions, deletions):
        return {
            "[Contributors Top-100] Average commits": commits/self.total,
            "[Contributors Top-100] Average participation weeks": weeks/self.total,
            "[Contributors Top-100] Average additions": additions/self.total,
            "[Contributors Top-100] Average deletions": deletions/self.total,
        }