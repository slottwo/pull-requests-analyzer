import github
from time import sleep, time as now

class GithubAccess:
    def __init__(self, tokens: list, wait=False):
        self.tokens = tokens if len(tokens) > 0 else [None]
        self.index = 0
        print(f'Setting token to: {self.tokens[0]}')
        self.access = github.Github(self.tokens[0])
        self.usable_tokens = [bool(github.Github(t).rate_limiting[0]) for t in self.tokens] 
        self.wait = wait

    
    def regenerate(self):
        self.access = github.Github(self.tokens[self.index])

    
    def update_tokens(self, api_requests: int):
        self.usable_tokens = [github.Github(t).rate_limiting[0] > api_requests for t in self.tokens]
    

    def next_token(self):
        try:
            self.index = self.usable_tokens[self.index:].index(True)
            print(f'Changing token to: {self.tokens[self.index]}')
            self.regenerate()
            return True
        except ValueError:
            return False
        

    def check_limit(self, api_requests: int):
        self.update_tokens(api_requests)
        if self.usable_tokens[self.index] == True:
            return True
        if self.next_token():
            return True
        if self.wait:
            timeskip = self.access.rate_limiting_resettime-now()
            print(f'Waitting: {timeskip//3600}h{timeskip%3600//60}min{timeskip%3600%60}s')
            sleep(timeskip)
            self.usable_tokens = [True]*len(self.usable_tokens)
            return True
        else:
            return False