#!/usr/bin/env python
# coding: utf-8

import os
import json
import logging
from datetime import datetime as dt
from flask import request,Flask
from requests.exceptions import Timeout
from flask_cors import CORS, cross_origin
import sentencevectormodel as sv
# to run flask
# in powershell $env:FLASK_APP = "main"
# set FLASK_ENV=development for development
# set FLASK_APP=main.py
# python -m flask run
#flask run --host 127.0.0.1 --port 5000

##############Initialising model with Local Model #############
USE_MODEL_FOLDER = 'USEModel'
path = os.path.join(os.getcwd(), USE_MODEL_FOLDER)
emb_model = sv.EmbeddingModel(USE=path)
word_embedding = sv.WordEmbedding(emb_model)

app = Flask(__name__)
CORS(app)

@app.route('/')
@cross_origin()
def base() :
	return "<h1>ML sentence encode API API</h1>"


@app.route('/use/getsentencevector', methods=['POST'])
@cross_origin()
def getsentencevector() :
    try :
        req = request.get_data().decode('utf-8')
        #print(req)
        sentences=json.loads(req)['sentences']
        res = word_embedding.getEmbedding_vector(sentences)
        return json.loads(json.dumps({'sentenceVector':  res}))
    
    except Timeout as ex:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return json.dumps({'error': str(ex)})
    except Exception as e:
        logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return json.dumps({'error': str(e)})
"""
@app.route('/em/', methods=['GET'])
@cross_origin()
def getfirstndataresponsibility():
	try:
		#k = request.args.get('k', type = int)
		#n = request.args.get('n', type = int)

	except Exception as e:
		return {}
"""



# main method start execution either in production or development mode

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
else:
    app.config.update(
        #SERVER_NAME='snip.snip.com:80',
        APPLICATION_ROOT='/',
    )