import flask
from flask import request, jsonify
import similar_articles
import json
import tldextract


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
    print(info.registered_domain)
    try:
        bias = name_to_stats[link_to_name[info.registered_domain]]["bias"]
        if(bias >= 25):
            bias_desc = 'Extreme Right'
        elif(bias >= 10):
            bias_desc = 'Right'
        elif(bias > 3):
            bias_desc = 'Slight Right'
        elif(bias <= -25):
            bias_desc = 'Far Left'
        elif(bias <= -10):
            bias_desc = 'Left'
        elif(bias < -3):
            bias_desc = 'Slight Left'
        else:
            bias_desc = 'Neutral'
    except KeyError:
        bias_desc = 'Neutral'
    return bias_desc

app.run()
