from utils import settings
from threading import Thread
import re
from github import Github
import __future__
from utils.CustomRequester import CustomRequester
from tqdm import tqdm
import brotli
import pickle
import pathlib
from concurrent.futures import ThreadPoolExecutor


class FakePaginatedList:
    def __init__(self, lst) -> None:
        self.lst = lst
        self.totalCount = len(lst)

    @property
    def reversed(self):
        lst2 = self.lst.copy()
        lst2.reverse()
        return FakePaginatedList(lst2)

    def __getitem__(self, key):
        return self.lst[key]


class BaseMetric:
    def __init__(self, link: str):
        if re.match(r'^[^\/]+\/[^\/]+$', link):
            self.repo_name = link
        else:
            if link[-1] == '/':
                link = link[0:-1]
            parts = link.split('/')[-2:]
            self.repo_name = "/".join(parts)

        github = Github(settings.TOKENS[0])
        github._Github__requester = CustomRequester()
        self._repo = github.get_repo(self.repo_name)

    def get_main_container(self, get_function):
        if (not self.dump_exists()) or settings.REFETCH:
            return get_function()

        if self.results_exist() and not settings.RECALCULATE:
            return FakePaginatedList([])
        else:
            return self.load_dump()

    def _calc(self, field, func):
        result = func()
        if type(result) is dict:
            for field, name in result.items():
                setattr(self, field, name)
        else:
            setattr(self, field, result)

    def _reducer(self, metrics, accumulator):
        tup = None
        for a, b in zip(metrics, accumulator):
            if not tup:
                tup = (a+b,)
            else:
                tup += (a+b,)
        return tup

    def dump_exists(self):
        repo_path = f'{settings.DUMP_PATH}/{self.repo_name.replace("/","_")}'
        file = f"{repo_path}/{self.__class__.__name__.lower()}.szhat"

        return pathlib.Path(file).exists()

    def dump_repo_file(self, data):
        repo_path = f'{settings.DUMP_PATH}/{self.repo_name.replace("/","_")}'
        file = f"{repo_path}/{self.__class__.__name__.lower()}.szhat"
        print(f"[{file}] Compressing...")
        pathlib.Path(f"{repo_path}").mkdir(parents=True, exist_ok=True)
        with open(file, "wb") as f:
            f.write(brotli.compress(pickle.dumps(data), quality=9))
        print(f"[{file}] Done compressing")

    def load_dump(self):
        repo_path = f'{settings.DUMP_PATH}/{self.repo_name.replace("/","_")}'
        file = f"{repo_path}/{self.__class__.__name__.lower()}.szhat"
        with open(file, "rb") as handler:
            print(f"[{file}] Unpacking...")
            data = handler.read()
            decompressed_data = brotli.decompress(data)
            array = pickle.loads(decompressed_data)
            print(f"[{file}] Done unpacking")
            return FakePaginatedList(array)

    def results_exist(self):
        file = f'{settings.RESULTS_PATH}/{self.repo_name.replace("/","_")}/{self.__class__.__name__}.pickle'
        return pathlib.Path(file).exists()

    def dump_results(self):
        path = f'{settings.RESULTS_PATH}/{self.repo_name.replace("/","_")}'
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        with open(f'{path}/{self.__class__.__name__}.pickle', 'wb') as handler:
            classname =self.__class__.__name__.lower()
            print(f"[{self.repo_name}] {classname} Done calculating; Saving...")
            pickle.dump(self, handler, protocol=pickle.HIGHEST_PROTOCOL)

    def calculate_info(self):
        from functools import reduce

        classname = self.__class__.__name__.lower()
        with (
            tqdm(total=self.total, position=settings.TQDM_MAPPING[classname]) as progress,
            ThreadPoolExecutor(max_workers=50) as t
            # ThreadPoolExecutor(max_workers=settings.WORKER_MAPPING[classname]) as t
        ):
            progress.set_description(
                f"[{self.repo_name}] {self.__class__.__name__.lower()} info calculation")

            def helper(el):
                progress.update()
                return self.accumulate(el)

            def metric_reducer(acc, metrics):
                return {key: metrics[key] + acc[key] for key in metrics.keys()}

            res = reduce(metric_reducer, t.map(helper, self.main_container))
            metrics = self.get_final_metrics(**res)
            for field, name in metrics.items():
                setattr(self, field, name)

    def calculate_metrics(self):

        if hasattr(self, "load") and (not self.dump_exists() or settings.REFETCH):
            classname = self.__class__.__name__.lower()
            with (
                tqdm(total=self.total, position=settings.TQDM_MAPPING[classname]) as load_progress,
                ThreadPoolExecutor(max_workers=50) as t
                ):
                load_progress.set_description(
                    f"[{self.repo_name}] {classname} load progress")

                def load_helper(el):
                    res =  self.load(el)
                    load_progress.update()
                    return res

                self.main_container = list(
                    t.map(load_helper, self.main_container))
                self.dump_repo_file(self.main_container)

        if not settings.RECALCULATE and self.results_exist():
            print(
                f"[{self.repo_name}] {self.__class__.__name__.lower()} is already calculated; Ignoring...")
            return

        #  Checking whether there are simple metrics to calculate
        if hasattr(self, "metrics") and settings.CALC_SIMPLE_METRICS:
            for field, metric in self.metrics.items():
                self._calc(field, metric)

        # Checking whether there are Iterator-tied metrics to calculate
        has_data_to_calc = hasattr(self, "main_container") and self.total
        needs_calculation = (not self.results_exist() or settings.RECALCULATE)
        if has_data_to_calc and needs_calculation and settings.CALC_COMPLEX_METRICS:
                print("started calc")
                self.calculate_info()

        # Removing non-metric fields
        delattr(self, "metrics")
        delattr(self, "_repo")
        self.__dict__.pop("total", None)
        self.__dict__.pop("main_container", None)

        self.dump_results()
