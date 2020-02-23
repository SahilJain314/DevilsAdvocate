import flask
from flask import request, jsonify
import similar_articles
import json
import tldextract
import tfPred
from newspaper import fulltext
import requests
import numpy as np


with open('linkToName.json', 'r') as f:
    link_to_name = json.load(f)

with open('nameToStats.json', 'r') as f:
    name_to_stats = json.load(f)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Political Bias API</h1>
<p>A prototype API for detecting political bias of text.</p>'''

@app.route('/vals.json', methods=['GET'])
def vals():
    with open('vals.json', 'r') as f:
        vals = json.load(f)['vals']
    return jsonify({
        "vals": vals
    })

@app.route('/api/bias/', methods=['GET'])
def api_id():

    if 'url' in request.args:
        url = str(request.args['url'])
        bb = get_bias(url)
        bias = bb[0]
        bias_desc = bb[1]
        print(bias_desc)

        if(bias_desc == 'Left'):
            n = 1
        elif(bias_desc == 'Moderate Left'):
            n = 2
        elif(bias_desc == 'Neutral'):
            n = 3
        elif(bias_desc == 'Moderate Right'):
            n = 4
        else:
            n = 5

        """
        f = open('C:/Users/sahil/Desktop/Files/Coding/PalyHacks-DevilsAdvocate/DevilsAdvocate/svg-doughnut-chart-with-animation-and-tooltip/dist/vals.js', 'r')    # pass an appropriate path of the required file
        lines = f.readlines()
        lines[n-1] = str(int(lines[n].split(',')[0]) + 1) + ",\n"  # n is the line number you want to edit; subtract 1 as indexing of list starts from 0
        f.close()   # close the file and reopen in write mode to enable writing to file; you can also open in append mode and use "seek", but you will have some unwanted old data if the new data is shorter in length.

        f = open('C:/Users/sahil/Desktop/Files/Coding/PalyHacks-DevilsAdvocate/DevilsAdvocate/svg-doughnut-chart-with-animation-and-tooltip/dist/vals.js', 'w')
        f.writelines(lines)
        # do the remaining operations on the file
        f.close()
        """
        with open('vals.json', 'r') as f:
            vals = json.load(f)['vals']

        vals[n - 1] = vals[n - 1] + 1

        with open('vals.json', 'w') as f:
            json.dump({"vals": vals}, f);

        try:
            all_articles = similar_articles.get(url)["articles"]
        except:
            return jsonify({
                'bias': bias_desc,
                'similar_articles': {"articles": []}
                })

        article_biases = []
        articles_biases_text = []

        for article in all_articles:
            print("article", article)
            b = get_bias_dict(article["url"])
            article_biases.append(b[0])
            articles_biases_text.append(b[1])
        article_biases = np.array(article_biases)

        if("Right" in bias_desc):
            k = min(3, len(article_biases) - 1)
            bs = np.argpartition(article_biases, k)[:k]
        elif("Left" in bias_desc):
            k = min(3, len(article_biases) - 1)
            bs = np.argpartition(-1 * article_biases, k)[:k]

        if("Neutral" in bias_desc):
            articles = all_articles
        else:
            articles = []
            for b in bs:
                print(tldextract.extract(all_articles[b]["url"]).registered_domain, tldextract.extract(url).registered_domain)
                if not(tldextract.extract(all_articles[b]["url"]).registered_domain == tldextract.extract(url).registered_domain):
                    articles.append(all_articles[b])

        return jsonify({
            'bias': bias_desc,
            'similar_articles': {"articles": articles}
            }
        )

    else:
        return "Error: No text field provided."

def get_bias(url):
    #info = tldextract.extract(url)

    b_dir = 0

    print(url)
    bias = 0
    try:
        html = requests.get(url).text
        text = fulltext(html)

        bias = tfPred.getDeepBias(text)
        bias[0] = bias[0]-.1
        bias[1] = bias[1]+.1
        b_dir = bias.argmax()
        print('b_dir: '+str(b_dir))
        b_mag = bias[b_dir]
        print(bias)
        bias = b_mag

    except:
        b_dir = 1
        bias = .5

    #print(info.registered_domain)
    try:
        #bias = name_to_stats[link_to_name[info.registered_domain]]["bias"]
        print('b_dir: '+str(b_dir))

        if b_dir == 1:
            if bias <.6:
                bias_desc = 'Neutral'
            elif(bias <.75):
                bias_desc = 'Moderate Right'
            else:
                bias_desc = 'Right'
        else:
            if bias <.6:
                bias_desc = 'Neutral'
            elif(bias <.75):
                bias_desc = 'Moderate Left'
            else:
                bias_desc = 'Left'
    except KeyError:
        bias_desc = 'Neutral'
    return bias, bias_desc

def get_bias_dict(url):
    info = tldextract.extract(url)
    print(info.registered_domain)
    bias = 0
    try:
        bias = name_to_stats[link_to_name[info.registered_domain]]["bias"]
        if(bias >= 10):
            bias_desc = 'Right'
        elif(bias > 3):
            bias_desc = 'Moderate Right'
        elif(bias <= -10):
            bias_desc = 'Left'
        elif(bias < -3):
            bias_desc = 'Moderate Left'
        else:
            bias_desc = 'Neutral'
    except KeyError:
        bias_desc = 'Neutral'
    return bias, bias_desc

app.run()
