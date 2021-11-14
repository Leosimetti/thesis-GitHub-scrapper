from utils.metrics.base  import BaseMetric
from datetime import datetime

class Meta(BaseMetric):

    def __init__(self, link: str):
        self.metrics = {
            "[Repo] Size": lambda: self._repo.size,
            "[Repo] Folders": self.get_folder_count,
            "[Repo] Files": self.get_file_count,
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
        super().__init__(link)
        self.calculate_metrics()
    
    def get_language_count(self):
        all_languages = self._repo.get_languages()
        all_lines = all_languages.values()
        total_lines = sum(all_lines)
        decent_languages = [lines for lines in all_lines if lines/total_lines >= 0.01]

        return len(decent_languages)
    
    def get_folder_count(self):
        def recursive_helper(file):
            if file.type == "dir":
                return 1 + sum(map(recursive_helper, self._repo.get_contents(file.path)))
            else: 
                return 0
                
        all_files = self._repo.get_contents("/")
        return sum(map(recursive_helper, all_files))

    def get_file_count(self):
        def recursive_helper(file):
            if file.type == "dir":
                return sum(map(recursive_helper, self._repo.get_contents(file.path)))
            else: 
                return 1 

        all_files = self._repo.get_contents("/")
        return sum(map(recursive_helper, all_files))
