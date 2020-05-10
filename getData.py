from datetime import datetime
import requests
import json
import time
import sys
import re

codeforcesURL = 'http://codeforces.com'

while True:
    try:
        contestGet = requests.get(codeforcesURL + '/api/contest.list?gym=false')
        contestGet.encoding = 'utf-8'
        contestList = contestGet.json()
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

with open('failed.csv', 'w') as failedCsv:
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
        blogRe = re.search(r'/blog/entry/([0-9]+)"[^>]*>Announcement[^<]*</a>', contestPage, re.M)
        if (blogRe):
            blogID = blogRe.group(1)
            print('The blog ID of the contest {} is {}'.format(contestid, blogID))
        else:
            print('Unable to get the announcement URL of the contest ' + contestid)
            sys.stdout.flush()
            failedCsv.write(contestid + '\n')
            continue
        while True:
            try:
                contestBlog = requests.get(codeforcesURL + '/api/blogEntry.view?blogEntryId=' + blogID).json()
            except:
                time.sleep(1)
            else:
                break
            print('Failed to get announcement blog of ' + contestid + ', retrying...')
            sys.stdout.flush()
        if contestBlog['status'] != 'OK':
            print('Failed to get the API of the blog ' + blogID)
            sys.stdout.flush()
            failedCsv.write(contestid + '\n')
            continue
        contestRating = contestBlog['result']['rating']
        print(contestid, contestRating)
        sys.stdout.flush()
        contests.append({'id': contestid,
                         'name': contest['name'],
                         'rating': contestRating,
                         'announcementID': blogID,
                         'announcementWriter': contestBlog['result']['authorHandle'],
                         'startTime': str(datetime.utcfromtimestamp(contest['startTimeSeconds']))})

contests.sort(key = lambda contest : contest['rating'], reverse = True)

with open('contests.json', 'w', encoding = 'utf-8') as contestJson:
    contestJson.write(json.dumps(contests, ensure_ascii=False))

with open('contests.csv', 'w', encoding = 'utf-8') as contestCsv:
    for key in contests[0]:
        contestCsv.write(key + ',')
    contestCsv.write('\n')
    for contest in contests:
        for key in contest:
            contestCsv.write('"' + str(contest[key]) + '",')
        contestCsv.write('\n')
