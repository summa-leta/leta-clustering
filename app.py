#!flask/bin/python
from __future__ import division
from flask import Flask, request, abort, jsonify
from collections import defaultdict
from gensim import corpora, models
import re
import os.path
import pickle

app = Flask(__name__)

state = {}
state_file = '/data/state.pickle'

data_dir = os.path.dirname(state_file)
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)


state['documents'] = {}
state['clusters'] = defaultdict(set)


if os.path.isfile(state_file):
    try:
        with open(state_file, 'r') as infile:
            state = pickle.load(infile)
    except:
        pass


def save_state():
    with open(state_file, 'w') as outfile:
        pickle.dump(state, outfile)


@app.route('/clear')
def clear():
    state['documents'] = {}
    state['clusters'] = defaultdict(set)
    save_state()
    return '{ "status": "clear" }'

dic = corpora.Dictionary.load('models/american-local-news.lower.150000_min=2_below=0.3_nostop.dic')
tfidf = models.tfidfmodel.TfidfModel.load('models/american-local-news.lower.tfidf')


def get_features(text):
    text_norm = ' '.join(re.split(r'\W+', text)).lower().strip()

    bow = dic.doc2bow(text_norm.split())
    bow = tfidf[bow]
    bow_top = sorted(bow, key=lambda x: x[1], reverse=True)[:100]

    features = {}
    for item in bow_top:
        features[item[0]] = item[1]

    return features


def distance(a, b):
    dividend = 0
    quotient = 0

    for i in a:
        dividend += a[i]
        if i in b:
            quotient += abs(a[i] - b[i])
        else:
            quotient += a[i]

    for i in b:
        dividend += b[i]
        if i not in a:
            quotient += b[i]

    return quotient / dividend


def get_similar_clusters(a):
    documents = state['documents']
    similar = set()

    for doc_id in documents:
        d = distance(a['topics'], documents[doc_id]['topics'])

        if d <= 0.678:
            similar.add(documents[doc_id]['cluster'])

    return similar


def set_cluster(old_cluster, new_cluster):
    clusters = state['clusters']
    documents = state['documents']

    clusters[new_cluster].update(clusters[old_cluster])
    for doc_id in clusters[old_cluster]:
        documents[doc_id]['cluster'] = new_cluster

    del clusters[new_cluster]


@app.route('/add', methods=['POST'])
def add():
    clusters = state['clusters']
    documents = state['documents']
    if not request.json or 'document' not in request.json:
        return jsonify(request.json)

    document = request.json['document']

    if document['id'] in documents:
        return jsonify({
            'cluster': documents[document['id']]['cluster'],
            'merged': []
        })

    document['topics'] = get_features(document['text'])

    similar = get_similar_clusters(document)

    if len(similar) == 1:
        cluster = similar.pop()
    else:
        cluster = len(clusters)

    clusters[cluster].add(document['id'])
    document['cluster'] = cluster

    for item in similar:
        set_cluster(item, cluster)

    documents[document['id']] = document

    save_state()

    return jsonify({
        'cluster': cluster,
        'merged': list(similar)
    })


@app.route('/')
def index():
    return "I'm listening"


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8001)
