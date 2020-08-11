import github
import csv

with open('input.csv', newline='') as csvfile:
    csv_reader = list(csv.reader(csvfile))
    token = csv_reader[0][0]
    ownerrepo_ls = tuple(csv_reader[1:])
    del csv_reader

g = github.Github(token)

for ownerrepo in ownerrepo_ls:
    output = {'total_merges': 0, 'total_rebases': 0, 'total_not_merged_pr': 0}

    repo = g.get_repo(ownerrepo)
    pulls = repo.get_pulls(state='closed')
    
    for pr in pulls:
        if pr.is_merged:
            output[pr.id] = {
                'merge_commit_sha': pr.merge_commit_sha,
                'base_sha': pr.base.sha,
                'data': pr.merged_at
            }
            if len(repo.get_commit(pr.merge_commit_sha).commit.parents) > 1:
                output[pr.id]['merge_or_rebase'] = 'merge'
                output['total_merges'] += 1
            else:
                output[pr.id]['merge_or_rebase'] = 'rebase'
                output['total_rebases'] += 1
        else:
            output['total_not_merged_pr'] += 1
    
    with open('output_by_repo.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([])
        del csvfile

    with open('output_total.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            ownerrepo,
            output['total_merges'],
            output['total_rebases'],
            output['total_not_merged_pr']
        ])
        del csvwriter
