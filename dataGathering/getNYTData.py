import requests
import json
import pickle
from sys import argv

NYT_api_key = 'e68cb4dbfc544ab9b8099f7333bb935e'

def getNYTMonth(year, month):
    request_url = 'https://api.nytimes.com/svc/archive/v1/{}/{}.json'.format(year, month)
    request_url += '?api-key=' + NYT_api_key
    response = requests.get(request_url)
    if not response.ok:
        return response
    json_response = json.loads(response.content)
    articles = [] # In format (Timestamp, Headline, Keywords)
    for doc in json_response['response']['docs']:
        try:
            key_words = []
            for key_word in doc['keywords']:
                key_words.append(key_word['value'])
            articles.append((doc['pub_date'], doc['headline']['main'], key_words))
        except KeyError:
            continue
    return articles

if __name__ == '__main__':
    start_month = int(argv[1])
    start_year = int(argv[2])
    end_month = int(argv[3])
    end_year = int(argv[4])

    all_articles = []

    while start_month != end_month or start_year != end_year:
        month_articles = getNYTMonth(start_year, start_month)
        print(len(month_articles), 'more articles loaded')
        all_articles.extend(month_articles)        
        
        start_month += 1
        if start_month >= 13:
            start_year += 1
            start_month = 1

    pickle.dump(all_articles, open('NYTArticles.pkl', 'wb'))
