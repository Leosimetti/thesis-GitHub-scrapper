from datetime import datetime
from typing import Counter
from github.Repository import Repository
from github.Stargazer import Stargazer
from github.StatsContributor import StatsContributor
from utils.metrics.base import BaseMetric



class Forks(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(self._repo.get_forks)
        self.total = self.main_container.totalCount

        self.metrics = {
            "[Forks] Count": lambda: self._repo.forks_count,
        }
        self.calculate_metrics()

    def load(self, fork: Repository):
        fork.created_at

        return fork

    def accumulate(self, fork: Repository):
        date = [fork.created_at]

        return {"dates": date,
                }

    def get_final_metrics(self, *, dates):
        unique_dates_values = Counter(dates).values()
        # total_dates = len(unique_dates_values)
        max_forks = max(unique_dates_values)
        age_days = (datetime.now() - self._repo.created_at).days


        return {
            # "forks_per_day_average": self.total/total_dates,
            "[Forks] Per day (True)": self.total/age_days,
            "[Forks] Max per day": max_forks,
        }