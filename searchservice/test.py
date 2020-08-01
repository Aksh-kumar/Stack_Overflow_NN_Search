#!/usr/bin/env python
# coding: utf-8


import sys
import os
import json
import logging
import time
import socket
import struct
from datetime import datetime as dt
from modules.elasticsearchconnection import ElasticSearchConnection
import modules.indexcreation as incrobj
from modules.essearch import ESSearch

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
        #PORT = int(CONSTCONFIG["socketPort"])
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

#load_constant()
#create_esconn_and_search_obj()

####################### API CALLS #####################
class QANDAESSearch:
    
    def __init__(self):
        load_constant()
        create_esconn_and_search_obj()
    
    
    # /es-search/get-answer/', methods=['GET']
    def get_answer_by_questionId(self, questionId: int)->object:
        try:
             
            res = SEARCHOBJ.get_matched_value(questionId, "parentId",
                                              CONSTCONFIG['answerIndexName'])
            
            return {'response': res, 'error': None}#json.dumps(res)
        
        except Exception as e:
            logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            return {'error': str(e), 'response': None }
    #End
    
    # '/es-search/get-tag/', methods=['GET']
    def get_tags_by_questionId(self, questionId: int)->object:
        try:
            
            res = SEARCHOBJ.get_matched_value(questionId, "questionId",
                                              CONSTCONFIG['tagIndexName'])
            
            return {'response': res, 'error': None}#json.dumps(res)
        
        except Exception as e:
            logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            return {'error': str(e), 'response': None }
    #End

    #'/es-search/search-sentence', methods=['POST']
    def search_sentence(self, request_data: object)->object:
        try :
            
            res = SEARCHOBJ.get_searched_result(request_data['sentence'],
                                                request_data['size'],
                                                request_data['withAnswer'],
                                                request_data['withTag'])
            return {'response': res, 'error': None}#json.dumps(res)
        
        except Exception as e:
            logging.exception(dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            return {'error': str(e), 'response': None }
    #End
    
    def request_and_response_root(self, request: object)->object:
        try:
            if request['methodName'] == 'get_answer_by_questionId':
                return self.get_answer_by_questionId(int(request['params']['questionId']))
            
            if request['methodName'] == 'get_tags_by_questionId':
                return self.get_answer_by_questionId(int(request['params']['questionId']))
            
            if request['methodName'] == 'search_sentence':
                return self.get_answer_by_questionId(request['params']['request_data'])
            
            return {'error': 'No method name signature matchesd', 'response': None }
        
        except Exception as e:
            return {'error': str(e), 'response': None }
#End



if __name__ == '__main__':
   #load_MLModel()
   #incrobj.load_index_data(CONSTCONFIG, ESCONNOBJ,word_embedding=EMBEDDING_MODEL)
   #res = get_answer_by_questionId(34676180)
   #print(res)
   obj = QANDAESSearch()
   body = {
           "sentence": "bert model find vector",
           "size": 5,
           "withAnswer": False,
           "withTag": False
         }
   
   """
   t1 = time.time()
   ob = QANDAESSearch()
   res=ob.search_sentence(body)
   t2 = time.time()
   print(t2-t1)"""
   




    