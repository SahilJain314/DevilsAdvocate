import flask
from flask import request, jsonify
import similar_articles
import json
import tldextract
import tfPred
from newspaper import fulltext
import requests


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

@app.route('/api/bias/', methods=['GET'])
def api_id():

    if 'url' in request.args:
        url = str(request.args['url'])
        bias_desc = get_bias(url)
        print(bias_desc)

        return jsonify({
            'bias': bias_desc,
            'similar_articles': similar_articles.get(url)
            }
        )

    else:
        return "Error: No text field provided."

def get_bias(url):
    info = tldextract.extract(url)

    print(url)

    try:
        html = requests.get(url).text
        text = fulltext(html)

        bias = tfPred.getDeepBias(text)
        b_dir = bias.argmax()
        b_mag = bias[b_dir]
        print(bias)
        bias = b_mag

    except:
        b_dir = 1
        bias = .5

    #print(info.registered_domain)
    try:
        #bias = name_to_stats[link_to_name[info.registered_domain]]["bias"]
        if b_dir is 1:
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
    return bias_desc

app.run()
