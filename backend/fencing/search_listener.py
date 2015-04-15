"""
Query for fencer in usfencing via monitoring firebase

Usage:
  search_listener.py <auth>
  search_listener.py -h | --help
  search_listener.py --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
"""
import datetime
from docopt import docopt

import datetime
import json
import firebase
import requests
from pprint import pprint
from search_fencing import search

query_url = 'fencein/membersToUpdate'

def patch_results(fencer):
    url = 'fencein/members'
    for member_number, data in fencer.items():
        url += '/' + member_number
        pprint(url)
        pprint(data)
        firebase.patch(url, data, auth=auth)


def delete_query(path):
    url = '/'.join((query_url, path))
    print(url)
    firebase.delete(url, auth=auth)


def search_fencer(data):
    protocol, change = data
    pprint(data)
    path = change['path']
    fencer = change['data']
    if type(fencer) == dict and ('memberNumber' in fencer or 'lastName' in fencer):
        query = fencer.get('memberNumber', fencer.get('lastName', None))
        if query is not None:
            try:
                res = search(query)
                pprint(res)
                patch_results(res)
            except Exception as e:
                try:
                    delete_query(path)
                except:
                    pass
                print(e)
            else:
                delete_query(path)
        else:
            delete_query(path)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    auth = args['<auth>']
    S = firebase.subscriber(query_url, search_fencer, auth=auth)
    S.start()
    S.wait()
