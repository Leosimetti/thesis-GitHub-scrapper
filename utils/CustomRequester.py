from github.Requester import Requester
from github import Github, RateLimitExceededException
from utils import settings
import time
from datetime import timedelta
from datetime import datetime
from collections import defaultdict
import random
from github.RateLimit import RateLimit

CURRENT_TIME_ZONE = 3

class CustomRequester(Requester):
    token_restores_at = defaultdict(lambda: datetime.now())

    def __init__(self):
        super().__init__(login_or_token=random.choice(settings.TOKENS),
                         password=None,
                         jwt=None,
                         base_url="https://api.github.com",
                         timeout=6666,
                         user_agent="PyGithub/Python",
                         per_page=100,
                         verify=True,
                         retry=None,
                         pool_size=None,)

    def perfrom_request(self, verb, url, parameters=None, headers=None, input=None):
        return self._Requester__check(
            *self.requestJson(
                verb, url, parameters, headers, input, self._Requester__customConnection(
                    url)
            )
        )

    def rate_limited(self):
        try:
            headers, data = self.perfrom_request("GET", "/rate_limit")
            limit = RateLimit(self, headers, data["resources"], True)
        except KeyError:
            print("Some weird RateLimit error🤮. Sleeping 60 sax...")
            time.sleep(60)
            return self.rate_limited()
        remaining = limit.core.remaining
        return remaining <= settings.TOKEN_LIMIT

    def get_current_token_reset_date(self):
        headers, data = self.perfrom_request("GET", "/rate_limit")
        limit = RateLimit(self, headers, data["resources"], True)
        return limit.core.reset + timedelta(hours=CURRENT_TIME_ZONE)

    def get_current_token(self):
        return self._Requester__authorizationHeader.split(" ")[1]

    def get_good_tokens(self):
        return [t for t in settings.TOKENS if self.token_restores_at[t] <= datetime.now()]

    def set_token(self, token):
        self._Requester__authorizationHeader = f"token {token}"

    def handle_no_tokens(self):
        closest_token = min(self.token_restores_at.items(), key=lambda x: x[1])[1]
        # print(f"😭😭😭 Closest usable token at {closest_token}")
        time.sleep(101)

    def set_valid_token(self):
        while True:
            good_tokens = self.get_good_tokens()
            random.shuffle(good_tokens)
            for token in good_tokens:
                self.set_token(token)
                
                if not self.rate_limited():
                    return
                token_idx = settings.TOKENS.index(token)
                reset_date = self.get_current_token_reset_date()
                self.token_restores_at[token] = reset_date
                # print(f"[Token {token_idx} ] Expired - will be reset at {reset_date}")

            self.handle_no_tokens()

    def requestJsonAndCheck(self, verb, url, parameters=None, headers=None, input=None):
        current_token = self.get_current_token()

        try:
            if self.rate_limited():
                self.token_restores_at[current_token] = self.get_current_token_reset_date()
                self.set_valid_token()
            return self.perfrom_request(verb, url, parameters, headers, input)

        except RateLimitExceededException:
            token_idx = settings.TOKENS.index(current_token)
            reset_date = datetime.now() + timedelta(minutes=8)
            self.token_restores_at[current_token] = reset_date
            # print(f"[Token {token_idx}] Secondary rate limit hit until {reset_date}!!!")
            
            if (good_tokens := self.get_good_tokens()):
                self.set_token(random.choice(good_tokens))
            else:
                self.handle_no_tokens()

            return self.requestJsonAndCheck(verb, url, parameters, headers, input)
