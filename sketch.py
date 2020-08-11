import github
import csv

with open('input.csv', newline='') as csvfile:
    reader = list(csv.reader(csvfile))
    token = reader[0][0]
    ownerrepo_ls = tuple(reader[1:])

total_merges = 0
total_rebases = 0
total_not_merged_pr = 0

g = github.Github(token)

for ownerrepo in ownerrepo_ls:
    repo = g.get_repo(ownerrepo)
    pulls = repo.get_pulls(state='closed')
    for pr in pulls:
        if pr.merged_at != None:
            total_rebases += 1
