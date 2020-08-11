from github import Github # To use Github API
import csv

# Input: A csv file with oauth-tokens on the 1st row and owner/repo's on the others rows
def input_file():
    with open('input.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        token = reader[0]
        ownerrepo_ls = tuple(reader[1:])
    return token, ownerrepo_ls


def get_pulls(github_access, ownerrepo):
    repo = github_access.get_repo(ownerrepo)
    pulls = repo.get_pulls(state='closed')
    return pulls


def main():
    token, ownerrepo_ls = input_file()
    g = Github(token)
    for ownerrepo in ownerrepo_ls:
        get_pulls(g, ownerrepo)
    pass


if __name__ == "__main__":
    main()
