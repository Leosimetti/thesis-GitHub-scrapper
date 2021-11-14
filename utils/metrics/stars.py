from datetime import datetime
from typing import Counter
from github.Stargazer import Stargazer
from github.StatsContributor import StatsContributor
from utils.metrics.base import BaseMetric



class Stars(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(self._repo.get_stargazers_with_dates)
        self.total = self.main_container.totalCount

        self.metrics = {
            "[Stars] Count": lambda: self._repo.stargazers_count
        }
        self.calculate_metrics()

    def load(self, stargazer: Stargazer):
        stargazer.starred_at

        return stargazer

    def accumulate(self, stargazer: Stargazer):
        date = [stargazer.starred_at]

        return {"dates": date,
                }

    def get_final_metrics(self, *, dates):
        unique_dates_values = Counter(dates).values()
        total_dates = len(unique_dates_values)
        max_stargazers = max(unique_dates_values)
        age_days = (datetime.now() - self._repo.created_at).days


        return {
            "[Stars] Per day": self.total/total_dates,
            "[Stars] Per day (True)": self.total/age_days,
            "[Stars] Maximum per day": max_stargazers,
        }