#!/usr/bin/env python
# coding: utf-8

import os
import json
import sys
import logging
from datetime import datetime as dt
from flask import request,Flask, jsonify
from flask_cors import CORS, cross_origin
from modules.elasticsearchconnection import ElasticSearchConnection
import modules.indexcreation as incrobj
from modules.essearch import ESSearch

# to run flask
# in powershell $env:FLASK_APP = "main"
# set FLASK_ENV=development for development
# set FLASK_APP=main.py
# python -m flask run
#flask run --host 127.0.0.1 --port 5001

##############Initializing  #############
ES_CONFIG_PATH = os.path.abspath('./config/esconfig.json')
TEXT_VECTOR_API = os.path.abspath('./config/textvectorconfig.json')
CONST_CONFIG_PATH = os.path.abspath('./config/constants.json') 

ESCONFIG = None
CONSTCONFIG = None
TEXT_VECTOR_API_URL = None

esobj = ElasticSearchConnection()
EMBEDDING_MODEL = None
ESCONNOBJ = None
SEARCHOBJ = None

def load_constant():
    global ESCONFIG, CONSTCONFIG, TEXT_VECTOR_API_URL
    
    try:
        with open(ES_CONFIG_PATH) as esf:
            ESCONFIG = json.load(esf)
        
        with open(TEXT_VECTOR_API) as tvf:
            TEXT_VECTOR_API_URL = json.load(tvf)
            
        with open(CONST_CONFIG_PATH) as ccf:
            CONSTCONFIG = json.load(ccf)
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        raise Exception(e)
# End

def load_MLModel():
    try:
        global EMBEDDING_MODEL
        
        sys.path.append(CONSTCONFIG['USEModelPath'])
        sys.path.append(CONSTCONFIG['SVModelPath'])
        import sentencevectormodel as sv
        
        emb_model = sv.EmbeddingModel(USE=CONSTCONFIG['USEModelPath'])
        EMBEDDING_MODEL = sv.WordEmbedding(emb_model)
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        raise Exception(e)
#End

def create_esconn_and_search_obj():
    try:
        global ESCONNOBJ, SEARCHOBJ
        ESCONNOBJ = esobj.get_conn_object(ESCONFIG['elasticSearchHost'], int(ESCONFIG['elasticSearchPort']))
        SEARCHOBJ = ESSearch(ESCONNOBJ, TEXT_VECTOR_API_URL['textVectorPOSTAPI'], CONSTCONFIG)
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        raise Exception(e)
#End

load_constant()
create_esconn_and_search_obj()

app = Flask(__name__)
CORS(app)

@app.route('/')
@cross_origin()
def base() :
    return "<h1>elastic search API</h1>"

@app.route('/es-search/get-answer/', methods=['GET'])
@cross_origin()
def get_answer_by_questionId():
    try:
        questionId = request.args.get('questionId', type = int)
        res = SEARCHOBJ.get_matched_value(questionId, "parentId",
                                          CONSTCONFIG['answerIndexName'])
        return jsonify(res)#json.dumps(res)
    
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return jsonify({'error': str(e)})#json.dumps({'error': str(e)})
#End

@app.route('/es-search/get-tag/', methods=['GET'])
@cross_origin()
def get_tags_by_questionId():
    try:
        questionId = request.args.get('questionId', type = int)
        res = SEARCHOBJ.get_matched_value(questionId, "questionId",
                                          CONSTCONFIG['tagIndexName'])
        return jsonify(res)#json.dumps(res)
    
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return jsonify({'error': str(e)})#json.dumps({'error': str(e)})
#End

@app.route('/es-search/search-sentence', methods=['POST'])
@cross_origin()
def search_sentence() :
    try :
        req = request.get_data().decode('utf-8')
        request_data =json.loads(req)
        res = SEARCHOBJ.get_searched_result(request_data['sentence'],
                                            request_data['size'],
                                            request_data['withAnswer'],
                                            request_data['withTag'])
        return jsonify(res)#json.dumps(res)
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return jsonify({'error': str(e)})#json.dumps({'error': str(e)})
#End

# main method start execution either in production or development mode

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
else:
    app.config.update(
        #SERVER_NAME='snip.snip.com:80',
        APPLICATION_ROOT='/',
    )