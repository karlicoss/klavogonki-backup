#!/usr/bin/env python3
import sys
import time
from datetime import datetime
from datetime import timedelta
from itertools import islice

from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore

from bs4 import BeautifulSoup # type: ignore

UID = sys.argv[1]

driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver')


# arbitrary
TO = '2100-01-01'
FROM = '2000-01-01'

def get_json(url):
    driver.get(url)
    time.sleep(1)
    text = BeautifulSoup(driver.page_source, 'lxml').body.text
    return eval(text.replace(':true', ':True').replace(':false', ':False').replace(':null', ':None'))

def get_overview(uid):
    return get_json(f'http://klavogonki.ru/api/profile/get-stats-overview?userId={uid}')


def get_mode_stats(uid, mode):
    return get_json(f'http://klavogonki.ru/api/profile/get-stats-details-data?userId={uid}&gametype={mode}&fromDate={FROM}&toDate={TO}&grouping=day')

def get_day_stats(uid, mode, dt):
    return get_json(f'http://klavogonki.ru/api/profile/get-stats-details-data?userId={uid}&gametype={mode}&fromDate={dt}&toDate={dt}&grouping=none')


def get_all(uid):
    res = {}
    overview = get_overview(uid)
    for gtype, gg in islice(overview['gametypes'].items(), None):
        gname = gg['name']
        by_day = get_mode_stats(uid, gtype)['list']
        handled = set()
        mode_items = []
        for d in islice(by_day, None):
            ts = d['min_date']['sec']
            d = datetime.fromtimestamp(ts)

            # ugh, unclear how they handled timezones
            dates = [d - timedelta(days=1), d, d + timedelta(days=1)]

            datess = [i.strftime('%Y-%m-%d') for i in dates]
            for ds in datess:
                print(gtype, ds)
                if ds in handled:
                    continue
                handled.add(ds)

                dstats = get_day_stats(uid, gtype, ds)
                mode_items.extend(dstats['list'])
        res[gname] = mode_items
    return res

def main():
    js = get_all(UID)
    from kython import json_dump_pretty
    with open('klavogonki.json', 'w') as fo:
        json_dump_pretty(fo, js)

if __name__ == '__main__':
    main()
