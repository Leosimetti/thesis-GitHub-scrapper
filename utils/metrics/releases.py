from datetime import datetime
from github.GitRelease import GitRelease
from github.StatsContributor import StatsContributor
from utils.metrics.base import BaseMetric
from tqdm import tqdm
from functools import reduce
from concurrent.futures import ThreadPoolExecutor


class Releases(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)
        self.main_container = self.get_main_container(self._repo.get_releases)
        self.total = self.main_container.totalCount

        self.metrics = {
            "[Releases] Count": lambda: self.total,
            "[Releases] Tags": lambda: self._repo.get_tags().totalCount,
        }
        self.calculate_metrics()

    def load(self, release: GitRelease):
        release.body
        release.title
        release.tag_name
        release.draft
        release.prerelease
        release.created_at
        release.published_at

        assets = release.get_assets()
        for asset in assets:
            asset.name
            asset.label
            asset.content_type
            asset.size
            asset.download_count
            
        release.assets = list(assets)

        return release
    
    def accumulate(self, release: GitRelease):
        body_len = len(release.body) if release.body else 0
        title_len = len(release.title) if release.title else 0
        create_date = release.created_at.date()
        publish_date = release.published_at.date()
        assets = len(release.assets)
        asset_downloads = sum(asset.download_count for asset in release.assets)
        asset_sizes = sum(asset.size for asset in release.assets)

        return {
            "body_len": body_len,
            "title_len": title_len,
            # "drafts": release.draft,
            "prereleases": release.prerelease,
            "create_dates": [create_date],
            "publish_dates": [publish_date],
            "assets": assets,
            "asset_downloads": asset_downloads,
            "asset_sizes": asset_sizes,
        }

    def get_final_metrics(self, *, body_len, title_len, prereleases, create_dates, publish_dates, assets, asset_downloads, asset_sizes):
        unique_create_dates= len(set(create_dates))
        unique_publish_dates= len(set(publish_dates))
        age_days = (datetime.now() - self._repo.created_at).days

        return {
            "[Releases] Total downloads": asset_downloads,
            "[Releases] Average body len (chars)": body_len/ self.total,
            "[Releases] Average title len (chars)": title_len/self.total,
            "[Releases] Average assets": assets/self.total,
            "[Releases] Average asset downloads": asset_downloads/assets if assets else 0,
            "[Releases] Average asset size": asset_sizes/assets if assets else 0,
            # "[Releases] Drafts to total": drafts/self.total,
            "[Releases] Prereleases to total": prereleases/self.total,
            "[Releases] Per day created (True)": unique_create_dates/age_days,
            "[Releases] Per day published (True)": unique_publish_dates/age_days,
            "[Releases] Downloads per day (True)": asset_downloads/age_days,
        }