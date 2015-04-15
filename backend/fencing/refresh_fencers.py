"""
Download usfencing membership and upload to firebase

Usage:
  refresh_fencers.py [--interval=INTERVAL] <auth>
  refresh_fencers.py -h | --help
  refresh_fencers.py --version

Options:
  -i INTERVAL, --interval=INTERVAL  Interval in seconds between downloads [default: 86400]
  -h --help                         Show this screen.
  --version                         Show version.
"""
import datetime
from docopt import docopt
import io
import os
import pandas as pd
import requests
from robobrowser import RoboBrowser
import requests
import sched
import sys
import time


def upload_fencers(session, auth, fencer):
    data = fencer.to_json(orient='index', date_format='iso')
    url = 'https://fencein.firebaseio.com/members.json'
    params = {'print': 'silent', 'auth': auth}
    session.put(url, data=data, params=params)


def download_members():
    browser = RoboBrowser()
    url = 'http://www.usfencing.org/page/show/698125-current-membership-listing'
    browser.open(url)
    link = browser.find('h3', {'class': 'iconCsv iconSizeM'}).find('a').attrs['href']
    print('Found link: {0}'.format(link))
    res = requests.get(link)
    f = io.StringIO(res.content.decode('latin1'))
    return f

def csv_to_df(file):
    columns = ['Last Name', 'First Name', 'Middle Name', 'Suffix', 'Nickname', 'Gender', 'Division', 'Section', 'Club 1 Name', 'Club 1 Abbreviation', 'Club 1 ID#', 'Club 2 Name', 'Club 2 Abbreviation', 'Club 2 ID#', 'Member #', 'Competitive', 'Expiration', 'Saber', 'Epee', 'Foil', 'US Citizen', 'Permanent Resident', 'Representing Country']

    df = pd.read_csv(file, encoding='latin1', parse_dates=['Expiration'], true_values=['Yes', "Competitive"], false_values=['No', "Non-Competitive"], index_col=['Member #'])

    column_names = {"Club 1 Abbreviation":  "Club_1_Abbreviation".lower(), "Club 1 ID#": "Club_1_ID".lower(), "Club 1 Name": "Club_1_Name".lower(), "Club 2 Abbreviation":  "Club_2_Abbreviation".lower(), "Club 2 ID#": "Club_2_ID".lower(), "Club 2 Name": "Club_2_Name".lower(), "Competitive": "Competitive".lower(), "Division": "Division".lower(), "Epee": "Epee_rating".lower(), "Expiration": "Expiration".lower(), "First Name":  "First_Name".lower(), "Foil":  "Foil_rating".lower(), "Gender": "Gender".lower(), "Last Name": "Last_Name".lower(), "Member Type": "Membership_Type".lower(), "Middle Name": "Middle_Name".lower(), "Nickname": "Nickname".lower(), "Permanent Resident": "Permanent_Resident".lower(), "Representing Country": "Representing_Country".lower(), "Saber": "Saber_rating".lower(), "Section": "section", "Suffix": "suffix", "US Citizen": "US_Citizen".lower()}
    df = df.rename(columns=column_names)
    return df


def refresh_fencers(sc, interval, session, auth):
    print('Refreshing fencers')

    start = time.time()
    file = download_members()
    download_time = time.time() - start
    print('CSV downloaded in {0} seconds'.format(download_time))

    df = csv_to_df(file)
    print('CSV converted; contains {0} fencers'.format(len(df)))

    print('Uploading fencers')
    start = time.time()
    upload_fencers(session, auth, df)
    upload_time = time.time() - start
    print('Fencers uploaded in {0} seconds'.format(upload_time))

    next_update = datetime.datetime.fromtimestamp(time.time() + interval).strftime('%Y-%m-%d %H:%M:%S')
    print('Next update at {0}'.format(next_update))
    sc.enter(interval, 1, refresh_fencers, (sc, interval, session, auth))


def loop(auth, interval):
    session = requests.Session()
    sc = sched.scheduler(time.time, time.sleep)
    # Immediately download.  The fencer func will refresh every interval
    sc.enter(0, 1, refresh_fencers, (sc, interval, session, auth))
    sc.run()

if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    auth = args['<auth>']
    interval = int(args['--interval'])
    loop(auth, interval)
