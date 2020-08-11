import github
import csv

with open('input.csv', newline='') as csvfile:
    reader = list(csv.reader(csvfile))
    token = reader[0][0]
    ownerrepo_ls = tuple(reader[1:])

total_merges = 0
total_rebases = 0
total_not_merged_pr = 0

output = dict()

g = github.Github(token)

for ownerrepo in ownerrepo_ls:
    output[ownerrepo] = {}

    repo = g.get_repo(ownerrepo)
    pulls = repo.get_pulls(state='closed')
    
    for pr in pulls:
        if pr.is_merged:
            output[ownerrepo][pr.id] = {
                'merge_commit_sha': pr.merge_commit_sha,
                'base_sha': pr.base.sha,
                'data': pr.merged_at
            }
            if len(repo.get_commit(pr.merge_commit_sha).commit.parents) > 1:
                output[ownerrepo][pr.id]['merge_or_rebase'] = 'merge'
                total_merges += 1
            else:
                total_rebases += 1
                output[ownerrepo][pr.id]['merge_or_rebase'] = 'rebase'
        else:
            total_not_merged_pr += 1

with open('output_by_repo.csv', 'w', newline='') as csvfile:
    pass

with open('output_by_repo.csv', 'w', newline='') as csvfile:
    pass
