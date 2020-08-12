import github
import csv

with open('input.csv', newline='') as csvfile:
    csv_reader = list(csv.reader(csvfile))
    token = csv_reader[0][0]
    ownerrepo_ls = tuple(csv_reader[1:][0])
    del csv_reader
print(token)
print(ownerrepo_ls)

g = github.Github(token)

for ownerrepo in ownerrepo_ls:
    pr_analysis = dict()
    total_pr = {'total_merges': 0, 'total_rebases': 0, 'total_not_merged_pr': 0}

    repo = g.get_repo(ownerrepo)
    pulls = repo.get_pulls(state='closed')
    
    for pr in pulls:
        if pr.is_merged:
            pr_analysis[pr.id] = {
                'merge_commit_sha': pr.merge_commit_sha,
                'base_sha': pr.base.sha,
                'data': pr.merged_at
            }
            if len(repo.get_commit(pr.merge_commit_sha).commit.parents) > 1:
                pr_analysis[pr.id]['merge_or_rebase'] = 'merge'
                total_pr['total_merges'] += 1
            else:
                pr_analysis[pr.id]['merge_or_rebase'] = 'rebase'
                total_pr['total_rebases'] += 1
        else:
            total_pr['total_not_merged_pr'] += 1

    with open(ownerrepo.replace('/', '-') + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['merged_commit_sha', 'base_sha', 'date', 'merge_or_rebase'])
        for pr in pr_analysis.values():
            csvwriter.writerow(list(pr.values()))
        del csvfile
    
    with open('total_pr_analysis.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['owner/repo','total_merges','total_rebases','total_not_merged_pull_requests'])
        csvwriter.writerow([
            ownerrepo,
            total_pr['total_merges'],
            total_pr['total_rebases'],
            total_pr['total_not_merged_pr']
        ])
        del csvwriter
