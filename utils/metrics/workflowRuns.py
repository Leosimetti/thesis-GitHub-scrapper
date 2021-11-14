from datetime import datetime
from utils.metrics.base import BaseMetric
from github.WorkflowRun import WorkflowRun
from tqdm import tqdm


class WorkflowRuns(BaseMetric):

    def __init__(self, link: str):
        super().__init__(link)

        self.main_container = self.get_main_container(self._repo.get_workflow_runs)
        self.total = self.main_container.totalCount

        successes = self._repo.get_workflow_runs(status="success").totalCount
        failures = self._repo.get_workflow_runs(status="failure").totalCount
        skipped = self._repo.get_workflow_runs(status="skipped").totalCount
        

        self.metrics = {
            "[Workflow Runs] Count": lambda: self.total,
            
            "[Workflow Runs] Successful to total": lambda:
                successes/self.total if self.total else 0,

            "[Workflow Runs] Failed to total": lambda:
                failures/self.total if self.total else 0,

            "[Workflow Runs] Skipped to total": lambda:
                skipped/self.total if self.total else 0,
        }
        self.calculate_metrics()

    def load(self, workflow: WorkflowRun):
        workflow.conclusion
        workflow.created_at
  
        try:
            duration = workflow.timing()[1]
        except IndexError:
            duration = 0
        workflow.duration = duration

        return workflow

    def accumulate(self, workflow):
        success_date = [workflow.created_at.date(
        )] if workflow.conclusion == "success" else []
        fail_date = [workflow.created_at.date(
        )] if workflow.conclusion == "failure" else []

        success_duration = 0
        failure_duration = 0
        match workflow.conclusion:
            case "success":
                success_duration = workflow.duration
            case "failure":
                failure_duration = workflow.duration

        return {
            "success_duration": success_duration,
            "failure_duration": failure_duration,
            "duration": workflow.duration,
            "success_dates": success_date,
            "failure_dates": fail_date,
        }

    def get_final_metrics(self, *, duration, success_duration, failure_duration, success_dates, failure_dates):
        successes = self._repo.get_workflow_runs(status="success").totalCount
        failures = self._repo.get_workflow_runs(status="failure").totalCount
        unique_success_dates = len(set(success_dates))
        unique_fail_dates = len(set(failure_dates))
        age_days = (datetime.now() - self._repo.created_at).days

        return {
            "[Workflow Runs] Average duration (ms)": duration/successes,
            "[Workflow Runs] Average success duration (ms)": success_duration/successes,
            "[Workflow Runs] Average failure duration (ms)": failure_duration/successes,
            "[Workflow Runs] Average successes per day": successes/unique_success_dates,
            "[Workflow Runs] Average successes per day (True)": successes/age_days,
            "[Workflow Runs] Average fails per day": failures/unique_fail_dates if failures else None,
            "[Workflow Runs] Average fails per day (True)": failures/age_days if failures else None,
        }
