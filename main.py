import github  # To use Github API
import csv  # To manage the input and output
from sys import exc_info

def input_file():
    """Take a csv file from project's root folder named 'input.csv', read it, then return the token (if any) and the full name repositories
    
    Returns:
        tuple[str or NoneType, list]: A token to access the Github API and a list of repositories to be analyzed
    """
    try:
        with open('input.csv', newline='') as file:
            reader = list(csv.reader(file))
            if '/' in reader[0][0]:
                token = None
                full_name_repo_ls = [x[0] for x in reader]
            else:
                token = reader[0][0]
                full_name_repo_ls = [x[0] for x in reader[1:]]
    except FileNotFoundError:
        print('Error: Input file (input.csv) not found! See <https://github.com/slottwo/pull-request-analyzer> to more information.')
        exit()
    except:
        print('Unexpected error:', exc_info()[0])
        print('Please report in: <https://github.com/slottwo/pull-requests-analyzer/issues>.')
        exit()
    return token, full_name_repo_ls


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

def output_by_repo(full_name: str, pr_analyses: list):
    """Create a file named with the repository full_name 

    Args:
        full_name (str): Repository full name in format 'owner/repo'
        pr_analysis (list[dict]): Pull requests analyses
    """
    file_name = full_name.replace('/', '_')
    title_row = ['merged_commit_sha','base_sha','date','merge_or_rebase']
    new_rows = [list(pr_analysis.values()) for pr_analysis in pr_analyses]
    csv_output(file_name, title_row, new_rows)


def output_total(total_ls: list):
    """Create a csv file named "total_output.csv" with the total values to each repository

    Args:
        total_ls (list[dict]): A list of dict with all analized repositories and your respective number total of merges, rebases and not merged pull requests
    """
    file_name = 'total_output'
    title_row = ['repository','total_merges','total_rebases','total_not_merged_pull_requests']
    new_rows = list(map(lambda d: d.values(), total_ls))
    csv_output(file_name, title_row, new_rows)


def get_integrated_pulls(repository: github.Repository.Repository, show_not_merged: bool = True):
    """Receives all integrated pull requests from a repository. And, optionally, count the non-integrated ones.

    Args:
        repository (github.Repository.Repository): Repository to recive pull requests from it
        show_not_merged (bool): Returns additionally the number of non-integrated pull requests

    Returns:
        list[PullRequest]: A list of PullRequests that have been integrated
        int (opitional): Number of non-integrated pull requests
    """
    # pulls = list(filter(lambda pull: pull.merged_at != None, repository.get_pulls(state='closed')))
    # if show_not_merged:
    #     return pulls
    # return pulls, len(filter(lambda pull: pull.merged_at == None, repository.get_pulls(state='closed')))
    pulls = list(repository.get_pulls(state='closed'))
    not_merged_count = 0
    for pull in pulls:
        if pull.merged_at == None:
            pulls.remove(pull)
            not_merged_count += 1
    if show_not_merged:
        return pulls, not_merged_count
    return pulls


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
    token, full_name_repo_ls = input_file()
    if token:
        g = github.Github(token)
    else:
        g = github.Github()
    total = list()
    for full_name in full_name_repo_ls:
        repo = g.get_repo(full_name)
        pulls, not_merged_pr_count = get_integrated_pulls(repo, show_not_merged=True)
        pull_analyses = []
        for pull in pulls:
            pull_analysis = {
                'merged_commit_sha': pull.merge_commit_sha,
                'base_sha': pull.base.sha,
                'date': pull.merged_at,
                'merge_or_rebase': 'rebase' if is_rebase(repo, pull) else 'merge'
            }
            pull_analyses.append(pull_analysis)
        total.append({
            'full_name': full_name,
            'total_merges': sum(map(lambda x: int('merge' in x.values()), pull_analyses)),
            'total_rebases': sum(map(lambda x: int('rebase' in x.values()), pull_analyses)),
            'total_not_merged_pr': not_merged_pr_count
        })
        output_by_repo(full_name, pull_analyses)
        print(total)
    output_total(total)


if __name__ == "__main__":
    main()
