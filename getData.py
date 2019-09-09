import requests
import json
import time
import sys
import re

codeforcesURL = 'http://codeforces.com'

while True:
    try:
        contestList = requests.get(codeforcesURL + '/api/contest.list?gym=false').json()
    except:
        time.sleep(1)
    else:
        if contestList['status'] == 'OK':
            break
    print('Failed to get contest list, retrying...')
    sys.stdout.flush()

print('Succesfully got the contest list.')
sys.stdout.flush()

contests = []

for contest in contestList['result']:
    contestid = str(contest['id'])
    while True:
        try:
            contestPage = requests.get(codeforcesURL + '/contest/' + contestid).text
        except:
            time.sleep(1)
        else:
            break
        print('Failed to get contest page of ' + contestid + ', retrying...')
        sys.stdout.flush()
    blogRe = re.search(r'/blog/entry/([0-9]*)"[^>]*>Announcement[^<]*</a>', contestPage, re.M)
    if (blogRe):
        blogID = blogRe.group(1)
    else:
        print('Unable to get the announcement URL of the contest ' + contestid)
        sys.stdout.flush()
        continue
    while True:
        try:
            contestBlog = requests.get(codeforcesURL + '/api/blogEntry.view?blogEntryId=' + blogID).json()
        except:
            time.sleep(1)
        else:
            if contestBlog['status'] == 'OK':
                break
        print('Failed to get announcement blog of ' + contestid + ', retrying...')
        sys.stdout.flush()
    contestRating = contestBlog['result']['rating']
    print(contestid, contestRating)
    sys.stdout.flush()
    contests.append({'id': contestid, 'name': contest['name'], 'rating': contestRating})

contests.sort(key = lambda contest : contest['rating'], reverse = True)

with open('contests.json', 'w') as contestJson:
    contestJson.write(json.dumps(contests))

with open('contests.csv', 'w') as contestCsv:
    for contest in contests:
        contestCsv.write(contest['id'] + ',"' + contest['name'] + '",' + str(contest['rating']) + '\n')
