# Credit to https://github.com/philipperemy/Reuters-full-data-set

import os
import pickle
import sys
from tqdm import tqdm
from datetime import timedelta, date, datetime

import bs4
import requests

def get_soup_from_link(link):
    if not link.startswith('http://www.reuters.com'):
        link = 'http://www.reuters.com' + link
    print(link)
    response = requests.get(link)
    assert response.status_code == 200
    return bs4.BeautifulSoup(response.content, 'html.parser')


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def run_full():
    today = datetime.now()
    output_dir = 'tmp_output_dump'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_date = date(int(sys.argv[2]), int(sys.argv[1]), 1)
    end_date = date(int(sys.argv[4]), int(sys.argv[3]), 1)
    iterations = 0
    for single_date in tqdm(date_range(start_date, end_date)):
        output = []
        string_date = single_date.strftime("%Y%m%d")
        link = 'http://www.reuters.com/resources/archive/us/{}.html'.format(string_date)
        try:
            soup = get_soup_from_link(link)
            targets = soup.find_all('div', {'class': 'headlineMed'})
        except Exception:
            print('EXCEPTION RAISED. Could not download link : {}. Resuming anyway.'.format(link))
            targets = []
        for target in targets:
            try:
                timestamp = str(string_date) + str(target.contents[1])
            except Exception:
                timestamp = None
                print('EXCEPTION RAISED. Timestamp set to None. Resuming.')
            title = str(target.contents[0].contents[0])
            href = str(target.contents[0].attrs['href'])
            output.append({'ts': timestamp, 'title': title, 'href': href})
            iterations += 1

        output_filename = os.path.join(output_dir, string_date + '.pkl').format(output_dir, string_date)
        with open(output_filename, 'wb') as w:
            pickle.dump(output, w)


if __name__ == '__main__':
    run_full()
