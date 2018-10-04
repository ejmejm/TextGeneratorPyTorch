# Website Fox search example: "http://www.foxnews.com/search-results/search?q=trump&ss=fn&sort=latest&type=story&min_date=2018-09-19&max_date=2018-09-20&start=0"

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from math import ceil
from time import time
import datetime
import sys

# Takes an average of ~4-6 seconds to get a response from a page

url_template = 'http://www.foxnews.com/search-results/search?q={}&ss=fn&sort=latest&type=story&min_date={}&max_date={}&start='

def parseHeadlines(parser):
    title_boxes = parser.find_all('h3')
    titles = []
    for title_box in title_boxes:
        titles.append(title_box.text.strip())
    return titles

def parseNumPages(parser):
    n_found_container = parser.find(class_='num-found ng-pristine ng-valid')
    n_found_text = n_found_container.text.strip()
    if n_found_text[0] == 'r':
        return 0
    n_found = int(n_found_text[:n_found_text.find(' ')])
    
    return ceil(n_found / 10.)

def genSearchUrl(query, start_date=None, end_date=None, start_year=None, start_month=None, start_day=None, end_year=None,\
                 end_month=None, end_day=None):
    if start_date is None and end_date is None:
        start_date = datetime.datetime(start_year, start_month, start_day)
        end_date = datetime.datetime(end_year, end_month, end_day)
    elif type(start_date) is str and type(end_date) is str:
        formatted_start_date = start_date
        formatted_end_date = end_date
    elif type(start_date) is datetime.datetime and type(end_date) is datetime.datetime:
        formatted_start_date = '{}-{}-{}'.format(start_date.year, start_date.month, start_date.day)
        formatted_end_date = '{}-{}-{}'.format(end_date.year, end_date.month, end_date.day)
    else:
        print('ERROR: Search URL incorrect format, must be a string or datetime object')
        
    return url_template.format(query, formatted_start_date, formatted_end_date)

def getFoxHeadlines(query, start_date=None, end_date=None, start_year=None, start_month=None, start_day=None, end_year=None,\
                 end_month=None, end_day=None):
    url = genSearchUrl(query, start_date, end_date, start_year, start_month, start_day, end_year, end_month, end_day)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url + '0')
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    headlines_all = parseHeadlines(soup)
    
    n_found = parseNumPages(soup)
    times = []
    
    for i in range(1, n_found):
        t = time()
        browser.get(url + str(int(i*10)))
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        page_headlines = parseHeadlines(soup)
        headlines_all.extend(page_headlines)
        times.append(time() - t)
    
    return list(set(headlines_all))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Please use the format, "python3 FoxScraper.py query year-month-day year-month-day"')
    else:
        print(getFoxHeadlines(sys.argv[1], sys.argv[2], sys.argv[3]))
    