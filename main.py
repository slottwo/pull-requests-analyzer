import subprocess as sp  # To use Github API
import json
import csv

# Input
# A csv file with oauth-tokens on the 1st row and owner/repo's on the others rows
def input_file():
    with open('input.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        tokens = tuple(reader[0])
        repo_ls = tuple(reader[1:])
    return tokens, repo_ls


def pr_json(token, repo_ls):
    pass


def main():
    TOKENS, REPO_LS = input_file()
    pr_json(TOKENS, REPO_LS)
    pass


if __name__ == "__main__":
    main()
