import requests
from newspaper import Article
import textrazor
from pprint import pprint
from datetime import datetime, timedelta
import json

def get(url = 'https://www.politico.com/news/2020/02/21/bernie-sanders-condemns-russian-116640'):

    article = Article(url)
#    characteristics = ['Location', 'Event', 'Person', 'Organization']
    article.download()
    article.parse()
    text = article.title
    date = article.publish_date
    days_to_subtract = 2
    try:
        d = (date - timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')
        d2 = (date + timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')
    except TypeError:
        date = datetime.now();
        d = (date - timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')
        d2 = (date + timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')

    alt_api_key = 'feca0c9db3d492ac63a83761a41d003f306c5acfff3b828b8c1319da'
    textrazor.api_key = '3db6ae4b1e8b2e04ee07657ca98d0de9eda7b885b3043dc11ab9b230'

    client = textrazor.TextRazor(extractors=["words", "phrases"])
    response = client.analyze(text)

    query = ''
    for np in response.noun_phrases():
        query += '{} '.format(text[np.words[0].input_start_offset: np.words[-1].input_end_offset])


    print(query)

    news_parameters = {
        'q': query,
        'from': d,
        'to': d2,
        'sortBy': 'popularity',
        'apiKey': 'a02790e5a3af4b5f8683318c276e702d'
    }

    response = requests.get('http://newsapi.org/v2/everything', params = news_parameters)
    json_data = json.loads(response.text)

    return json_data
