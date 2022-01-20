from utils.tokens import TOKENS, BANNED_TOKENS

TOKENS = BANNED_TOKENS + TOKENS
REFETCH = False
RECALCULATE = False
CALC_SIMPLE_METRICS = True
CALC_COMPLEX_METRICS = True

TOKEN_LIMIT = 15
LOAD_THREADS = 22

TQDM_MAPPING = {
    "commits" : 0,
    "issues"  : 1,
    "contributors": 2,
    "pulls": 3,
    "workflowruns": 4,
    "releases": 5,
    "stars": 6,
    "forks": 7
}

DUMP_PATH = "./dump"
RESULTS_PATH = "./intermediate"

