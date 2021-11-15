from concurrent.futures.thread import ThreadPoolExecutor
from utils.metrics.base  import BaseMetric
from datetime import datetime

class Meta(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)

        files, folders = self.get_content_metrics()
        self.metrics = {
            "[Repo] Size": lambda: self._repo.size,
            "[Repo] Folders": lambda: folders,
            "[Repo] Files": lambda: files,
            "[Repo] Topics": lambda: len(self._repo.get_topics()),
            "[Repo] Branches": lambda: self._repo.get_branches().totalCount,
            "[Repo] Age (days)": lambda: (datetime.now() - self._repo.created_at).days,
            "[Repo] Workflows": lambda: self._repo.get_workflows().totalCount,
            "[Repo] Programming Languages": self.get_language_count,
            "[Repo] Milestones": lambda: self._repo.get_milestones().totalCount,
            "[Repo] Watchers": lambda: self._repo.subscribers_count,
            "[Repo] Deployments": lambda: self._repo.get_deployments().totalCount,
            "[Repo] Readme length (chars)": lambda: len(self._repo.get_readme().content),
            "[Repo] Network members": lambda: self._repo.network_count,
        }
        self.calculate_metrics()
    
    def get_language_count(self):
        all_languages = self._repo.get_languages()
        all_lines = all_languages.values()
        total_lines = sum(all_lines)
        decent_languages = [lines for lines in all_lines if lines/total_lines >= 0.01]

        return len(decent_languages)
    
    def get_content_metrics(self):
        self.folders = 0

        def recursive_helper(file):
            if file.type == "dir":
                self.folders += 1
                return sum(map(recursive_helper, self._repo.get_contents(file.path)))
            else: 
                return 1
            
        root_contents = self._repo.get_contents("/")
        if type(root_contents is list):
            files, folders = sum(map(recursive_helper, root_contents)), self.folders
            delattr(self, "folders")
            return files, folders
        else:
            return 1, 0

