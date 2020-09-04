import github  # To use Github API
import csv  # To manage the input and output
from sys import exc_info
from time import sleep, strftime, mktime, localtime, time as now


def input_file(file_name: str):
    """Take a csv file from project's root folder named 'input.csv', read it, then return the token (if any) and the full name repositories
    
    Returns:
        tuple[list[str], list]: A token to access the Github API and a list of repositories to be analyzed
    """        
    try:
        with open(file_name + '.csv', newline='') as file:
            reader = list(csv.reader(file))
            full_name_repo_ls = [x[0] for x in reader]
            
        with open('tokens.csv', 'w', newline='') as file:  # w flag used to create a new file if there is no
            reader = list(csv.reader(file))
            tokens = [x[0] for x in reader]
    except FileNotFoundError:
        print(f'Error: Input file ({file_name}) not found! See <https://github.com/slottwo/pull-request-analyzer> to more information.')
        exit()
    except:
        print('Unexpected error:', exc_info()[0])
        print('Please report in: <https://github.com/slottwo/pull-requests-analyzer/issues>.')
        exit()
    return tokens, full_name_repo_ls


def csv_output(file_name: str, title_row: list, new_rows: list):
    """It opens (or creates), writes (adding new lines) and closes a csv file

    Args:
        file_name (str): Output file name withoud extension
        title_row (list): Row with the label of each column
        new_rows (list): New rows to be added
    """
    old_rows = []

    with open(file_name + '.csv', 'w', newline='') as file:
        # Reading
        reader = csv.reader(file)
        if reader.line_num != 0:  # Checks whether the file is not empty
            old_rows = list(reader)[1:]  # This is to not exclude them
        # Writing
        writer = csv.writer(file)
        writer.writerow(title_row)
        rows = old_rows[:]  # Copy old_rows elements to rows
        for row in new_rows: # This is if there are repeated lines
            if not row in old_rows:
                rows.append(row)
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
    title_row = ['repository','total_merges','total_rebases','total_not_merged_pull_requests']
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
    # pulls = list(filter(lambda pull: pull.merged_at != None, repository.get_pulls(state='closed')))
    # if show_not_merged:
    #     return pulls
    # return pulls, len(filter(lambda pull: pull.merged_at == None, repository.get_pulls(state='closed')))
    closed_pulls = list(repository.get_pulls(state='closed'))
    integrated_pulls = list()
    not_merged_count = 0
    for pull in closed_pulls:
        if pull.merge_commit_sha != None:
            integrated_pulls.append(pull)
        else:
            not_merged_count += 1
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
    return len(repo.get_commit(pull.merge_commit_sha).commit.parents) == 1


def main():
    tokens, full_name_repo_ls = input_file('repositories')
    if len(tokens) == 1:
        g = github.Github(tokens[0])
    else:  # Comming soon...
        g = [github.Github(t) for t in tokens]
    total = list()
    
    for full_name in full_name_repo_ls:
        # Getting repository as Repository instance 
        repo = g.get_repo(full_name)
        
        # Gettings integrated pulls requests list and how many pulls were not
        pulls, not_merged_pr_count = get_integrated_pulls(repo, show_not_merged=True)
        
        if len(pulls)*2 < g.rate_limiting[0]:
            pull_analyses = []
            for pull in pulls:
                pull_analysis = {
                    'merged_commit_sha': pull.merge_commit_sha,
                    'base_sha': pull.base.sha,
                    'date': pull.merged_at,
                    'merge_or_rebase': 'rebase' if is_rebase(repo, pull) else 'merge'
                }
                pull_analyses.append(pull_analysis)
                if len(pull_analyses) >= 200:
                    break
            
            total.append({
                'full_name': full_name,
                'total_merges': sum(map(lambda x: int('merge' in x.values()), pull_analyses)),
                'total_rebases': sum(map(lambda x: int('rebase' in x.values()), pull_analyses)),
                'total_not_merged_pr': not_merged_pr_count
            })
            output_repo(full_name, pull_analyses)
        else:
            resettime = g.rate_limiting_resettime
            formatedresettime = strftime('%Y-%m-%d %H:%M:%S', localtime(resettime))
            print(f'Limit reached. Do you want to wait until the reset time ({formatedresettime}) or exit?')
            print('1. Wait')
            print('2. Exit')
            while True:
                o = input('')
                if o == 1:
                    sleep((resettime-mktime(now())))
                    break
                elif o == 2:
                    exit()

    output_total(total)


if __name__ == "__main__":
    main()
