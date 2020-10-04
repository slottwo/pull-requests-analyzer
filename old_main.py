import github  # To use Github API
import csv  # To manage the input and output
from sys import exc_info
from time import sleep, strftime, mktime, localtime, time as now

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


def input_file(file_name: str):
    """Take a csv file from project's root folder named 'input.csv', read it, then return the token (if any) and the full name repositories
    
    Returns:
        tuple[list[str], list]: A token to access the Github API and a list of repositories to be analyzed
    """
    # Taking tokens
    try:
        with open('tokens.csv', newline='') as file:
            reader = list(csv.reader(file))
            tokens = {x[0] for x in reader}
    except FileNotFoundError:
        try:
            temp = open('tokens.csv', 'w+', newline='')
            del temp 
            input_file(file_name)
        except:
            print('Could not create a tokens.csv file')
            tokens = [None]
    
    try:
        with open(file_name, newline='') as file:
            reader = list(csv.reader(file))
            full_name_repo_ls = {x[0] for x in reader}
    except FileNotFoundError:
        print(f'Error: Input file not found! See <https://github.com/slottwo/pull-request-analyzer> to more information.')
        exit()
    except:
        print('Unexpected error:', exc_info()[0])
        print('Please report in: <https://github.com/slottwo/pull-requests-analyzer/issues>.')
        exit()
    
    # Taking repositories already analyzed and subtracting the ready from the new
    try:
        file = open('total_analysis.csv', newline='')
        reader = csv.reader(file)
    except FileNotFoundError:
        print('Could not find total_analysis.csv file')
    except:
        print('Could not open total_analysis.csv file')
    else:
        fn_repo_ls_analyzed = {x[0] for x in list(reader)[1:]}
        full_name_repo_ls = full_name_repo_ls - fn_repo_ls_analyzed
    
    return list(tokens), list(full_name_repo_ls)


def csv_output(file_name: str, title_row: list, new_rows: list):
    """It opens (or creates), writes (adding new lines) and closes a csv file

    Args:
        file_name (str): Output file name withoud extension
        title_row (list): Row with the label of each column
        new_rows (list): New rows to be added
    """
    # Reading
    old_rows = []  # Because 'w+' clear the file
    try:
        with open(file_name+'.csv', newline='') as file: # Reading without clear it
            reader = list(csv.reader(file))
            if len(reader) != 0:  # Checks whether the file is not empty
                old_rows = reader[1:]  # This is to not exclude them
    except FileNotFoundError:
        pass
    
    # Writing
    with open(file_name + '.csv', 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(title_row)  # Title
        rows = old_rows[:] + new_rows
        writer.writerows(rows)


def output_repo(full_name: str, pr_analyses: list):
    """Create a file named with the repository full_name 

    Args:
        full_name (str): Repository full name in format 'owner/repo'
        pr_analysis (list[dict]): Pull requests analyses
    """
    file_name = full_name.replace('/', '_')
    title_row = ['merged_commit_sha','base_sha','date','merge_or_rebase']
    new_rows = [list(pr_analysis.values()) for pr_analysis in pr_analyses]
    csv_output('analyses_per_repository/' + file_name, title_row, new_rows)


def output_total(total_ls: list):
    """Create a csv file named "total_output.csv" with the total values to each repository

    Args:
        total_ls (list[dict]): A list of dict with all analyzed repositories and your respective number total of merges, rebases and not merged pull requests
    """
    file_name = 'total_analysis'
    title_row = ['repository','total_merges','total_rebases','total_unknown','total_not_merged_pull_requests']
    new_rows = list(map(lambda d: d.values(), total_ls))
    csv_output(file_name, title_row, new_rows)


def get_integrated_pulls(repository: github.Repository.Repository, show_not_merged: bool = True):
    """Receives all integrated pull requests from a repository. And, optionally, count the non-integrated ones.

    Args:
        repository (github.Repository.Repository): Repository from which it will to receive pull requests
        show_not_merged (bool): Returns additionally the number of non-integrated pull requests

    Returns:
        list[PullRequest]: A list of PullRequests that have been integrated
        int (optional): Number of non-integrated pull requests
    """
    closed_pulls = list(repository.get_pulls(state='closed'))
    # pulls = list(filter(lambda pull: pull.merged_commit_at != None, closed_pulls))
    # if show_not_merged:
    #     return pulls
    # return pulls, len(closed_pulls) - len(pulls)
    print(f'Closed pulls getted ({len(closed_pulls)})')
    integrated_pulls = list()
    not_merged_count = 0
    for pull in closed_pulls:
        if pull.merge_commit_sha != None:
            integrated_pulls.append(pull)
        else:
            not_merged_count += 1
        if len(integrated_pulls) == 200:
            break
    print(f'Pulls were filtered (integrated: {len(integrated_pulls)}, not_merged: {not_merged_count})')
    if show_not_merged:
        return integrated_pulls, not_merged_count
    return integrated_pulls


def is_rebase(repo: github.Repository.Repository, pull: github.PullRequest.PullRequest):
    """Checks if the pull in question is the result of a rebase method according to the number of parents of your commit. If it is more than one, it is the result of a merge

    Args:
        repo (github.Repository.Repository): Pull-Request's repository
        pull (github.PullRequest.PullRequest): Pull-Request to be checked

    Returns:
        bool: Whether it's the result of rebase or merge method
    """
    try:
        commit = repo.get_commit(pull.merge_commit_sha)
    except:
        return 'unknown'
    else:
        return 'rebase' if len(commit.commit.parents) == 1 else 'merge'


def main():
    tokens, full_name_repo_ls = input_file('repositories.csv')
    
    g = GithubAccess(tokens, wait=True)
    print('Github API accessed')
    dict_count = lambda value, dictionaries: sum([list(d.values()).count(value) for d in dictionaries])
    
    for full_name in full_name_repo_ls:
        if not g.check_limit(401):  # get_repo: 1, get_integrated_pulls: ~200, is_rebase: 2*(200 or less)
            break
        print(f'Checked limit ({g.access.rate_limiting[0]})')
        
        # Getting repository as Repository instance 
        repo = g.access.get_repo(full_name)
        print(f'Repository {full_name} were getted')
        
        # Gettings integrated pulls requests list and how many pulls were not
        pulls, not_merged_pr_count = get_integrated_pulls(repo, show_not_merged=True)
        print(f'Integrated pulls were getted')
        
        if not g.check_limit(len(pulls)):  # This is in case it took more than 200 requests to generate the pulls and, if so, if there are still enough requests in the GithubAccess to be able to exchange the token (if any) or leave
            break
        print(f'Checked limit ({g.access.rate_limiting[0]})')
        
        pull_analyses = []
        for pull in pulls:
            pull_analysis = {
                'merged_commit_sha': pull.merge_commit_sha,
                'base_sha': pull.base.sha,
                'date': pull.merged_at,
                'merge_or_rebase': is_rebase(repo, pull)  # rebase, merge, unknown
            }
            
            pull_analyses.append(pull_analysis)
        
        print('Pulls were analyzed')
        
        output_repo(full_name, pull_analyses)
        
        print('Repository output were finalized')
        
        total = {'full_name': full_name, 
                 'total_merges': dict_count('merge', pull_analyses), 
                 'total_rebases': dict_count('rebase', pull_analyses), 
                 'total_commit_not_found': dict_count('unknown', pull_analyses), 
                 'total_not_merged_pr': not_merged_pr_count}
        
        output_total([total])


if __name__ == "__main__":
    main()
