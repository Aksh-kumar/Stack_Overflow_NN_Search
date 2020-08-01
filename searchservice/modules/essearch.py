# -*- coding: utf-8 -*-
"""
Created on Thu Jun  13 18:54:47 2020

@author: Akash Kumar
"""

import json
from typing import List, TypeVar, Iterable, Tuple
from elasticsearch import Elasticsearch
from modules.APIrequest import APIRequest

StrInt = TypeVar('StrInt', str, int)
StrList = TypeVar('StrList', str, List[str])

######## constant #################

RESPONSE_SIZE = 50
ANSWER_MAX_SIZE = 410
TAG_MAX_SIZE = 10

def check_size(func):
    def helper(*args):
        if args[2] is not None and args[2] > RESPONSE_SIZE:
            raise Exception("Size cannot be more then {0}".format(RESPONSE_SIZE))
        return func(*args)
    return helper
#End

class ESSearch:
    """used to search from es database"""
    
    def __init__(self, es: Elasticsearch, sentence_encoder_url: str, constobj: object):
        """
         initialization method

        Parameters
        ----------
        es : Elasticsearch
            elastic search connecion object.
        sentence_encoder_url: str
            ML sentence encoder Model url from where sentence is encoded (POST URL)
            expected object json {sentences: List[sentences]}
            return object {sentenceVector: List[List[float]]}
       constobj: object
           json object with all constant values
        
        Returns
        -------
        None.

        """
        self.es = es
        self.api = APIRequest()
        self.constant = constobj
        self.sentence_encoder_url = sentence_encoder_url
    
    
    def _get_sentence_vector(self, sentence: str)->List[float]:
        """
        to get sentence encoded vector

        Parameters
        ----------
        sentence : str
            senetence need to encoded.

        Returns
        -------
        List[float]
            float dense vector.

        """
        try:
            payload = json.dumps({"sentences": [sentence]})
            header = self.api.get_header('json')
            res = self.api.POST(self.sentence_encoder_url, payload, header)
            if not res:
                raise Exception("Some API related issue occured")
                return {}
            return res
        except Exception as e:
            raise Exception(e)
    
    
    def _get_multi_index_search(self, indexlist: list, bd: dict, response_size: int, timeout:int)->object:
        """
        fetch data from multiple indexes

        Parameters
        ----------
        indexlist : list
            List of index name.
        bd : dict
            body of query in json.
        response_size : int
            size of response from each indexes.
        timeout : int
            request time out .

        Returns
        -------
        object
            response object combine all.

        """
        res = self.es.search(index=indexlist[0], body=bd,
                             request_timeout=timeout, size=response_size)
        for i in range(1, len(indexlist)):
            temp =  self.es.search(index=indexlist[i], body=bd,
                             request_timeout=timeout, size=response_size)
            res['hits']['total']['value'] += temp['hits']['total']['value']
            if res['hits']['max_score'] < temp['hits']['max_score']:
                res['hits']['max_score'] = temp['hits']['max_score']
            res['hits']['hits'].extend(temp['hits']['hits'])
        
        res['hits']['hits'].sort(key=lambda x : x['_score'], reverse=True)
        
        if len(res['hits']['hits']) > response_size:
            res['hits']['hits'] = res['hits']['hits'][:response_size]
        return res
    
    
    def keyword_search(self, keyword:str, feild: str, index_name: StrList )->object:
        """
        keyword match based search
        Parameters
        ----------
        keyword : str
            keyword to search.
        feild : str
            column name of search parameter.
        index_name: StrList
            name or list of names of index
        
        Returns
        -------
        object
            response object.

        """
        try:
            bd={
                'query':
                    {'match': 
                         {
                             "{0}".format(feild): keyword
                        }
                    },
                'sort': 
                    {'_score':
                        {
                              'order': "desc" 
                        }
                    }
                }
            #bd['query']['match'][feild] = keyword
            #bd['sort'] =  { '_score': {'order': "desc" }}
            if isinstance(index_name, str):
                res = self.es.search(index=index_name, body=bd, size=RESPONSE_SIZE)
                return res
            if isinstance(index_name, list):
                res = self._get_multi_index_search(index_name, bd, RESPONSE_SIZE, 60)
                return res
        except Exception as e:
            raise Exception(e)
    
    
    def cosine_similarity_search(self, sentence: str,  feild: str, index_name: StrList)->object:
        """
        give cosine similarity search
        Parameters
        ----------
        sentence : str
            test which need to encoded in sentence vector
        feild : str
            column name of search parameter.
        index_name : StrList
            name or list of names of indexs.

        Raises
        ------
        Exception
            raise generic exception when API response is invalid.

        Returns
        -------
        object
            response from es db.

        """
        try:
            query_vector = None
            response = self._get_sentence_vector(sentence)
            
            if 'sentenceVector' in response:
                query_vector = response['sentenceVector'][0] # returned list but only one sentence given
            else:
                raise Exception("required sentence vector is not found")
            
            bd = {
                    "query" :
                      { "script_score" : 
                           { "query" : { "match_all": {}},
                             "script" : 
                                 {
                                    "source": "cosineSimilarity(params.query_vector, '{0}') + 1.0".format(feild),
                                    "params": {"query_vector": query_vector}
                                }
                           }
                      },
                  "sort": 
                      { '_score': 
                           {'order': "desc" }
                      }
                }
            
            if isinstance(index_name, str):
                res = self.es.search(index=index_name, body=bd, request_timeout=60, size=RESPONSE_SIZE)
                return res
            if isinstance(index_name, list):
                res = self._get_multi_index_search(index_name, bd, RESPONSE_SIZE, 60)
                return res
        except Exception as e:
            raise Exception(e)
    
    
    def get_matched_value(self, param: StrInt, column_name: str, index_name: str)->object:
        """
        search all document with given particular feild and value and returned matched document
        
        Parameters
        ----------
        param : StrInt
            search paramter which value need to search.
        column_name : str
            column name need to search on.
        index_name : str
            index name in which search begin.

        Returns
        -------
        object
            response object.

        """
        try:
            """
            bd = {
                    "query": {
                        "bool": {
                            "must": {
                                "match_all": {}
                            },
                        "filter": {
                            "term": {
                                "{0}".format(column_name): param
                                }
                            }
                        }
                    }
                }"""
            bd = {
                    "query": {
                        "bool": {
                            "must": {
                                "term": {
                                    "{0}".format(column_name): param
                                }
                        },
                        "filter": {
                            "term": {
                                "{0}".format(column_name): param
                                }
                            }
                        }
                    }
                }
            res = self.es.search(index=index_name, body=bd, size=max(ANSWER_MAX_SIZE, TAG_MAX_SIZE)) 
            return res
        
        except Exception as e:
            raise Exception(e)
    
    
    def _result_object(self, source_object: object, score: float,
                       score_type: str, with_answer: bool, with_tag: bool)->object:
        """
        return resultant object 

        Parameters
        ----------
        source_object : object
            object from source.
        score: float
            score value of object
        score_type: str
            type of score keyword search or nn search score
        with_answer : bool, optional
            response with answer included. The default is False.
        with_tag : bool, optional
            response with tag included. The default is False.

        Returns
        -------
        object
            resultant object.

        """
        def answerFormat(obj: object):
            if obj['_source']['ownerUserId'] == self.constant['ownerIDNULLValue']:
                obj['_source']['ownerUserId'] = None
            
            return obj['_source']
        #end
        
        del source_object['title_vector']
        if with_answer:
            temp = self.get_matched_value(source_object['id'],
                                          "parentId",
                                          self.constant['answerIndexName']
                                          )
            
            source_object['answer'] = list(map(answerFormat, temp['hits']['hits']))
        
        if with_tag:
            temp = self.get_matched_value(source_object['id'],
                                          "questionId",
                                          self.constant['tagIndexName']
                                          )
            
            source_object['tag'] = list(map(lambda x: x['_source'], temp['hits']['hits']))
       
        if source_object['ownerUserId'] == self.constant['ownerIDNULLValue']:
            source_object['ownerUserId'] = None
        
        if source_object['closedDate'] == self.constant['dateNULLValue']:
            source_object['closedDate'] = None
        
        source_object['keywordScore'] = None
        source_object['nnScore'] = None
        source_object[score_type] = score
        
        return source_object
    
    
    def _rescale(self, list_object: Iterable[object], feild: str,
                 old_range: Tuple[int, int], new_range: Tuple[int, int])->List[object]:
        """
        scale particular feild in all objects in lists
        
        Parameters
        ----------
        list_object : Iterable[object]
            list of object in which transformation need to apply.
        feild : str
            feild of object in which transformation apply.
        old_range: Tuple[int, int]
            old range of current data format (min, max) inclusive
        old_range: Tuple[int, int]
            new range of current data format (min, max) inclusive
        
        Returns
        -------
        object
            same object but with scaled value in 'feild' property.
        """
        
        try:
            
            old_range_diff = old_range[1]-old_range[0]
            new_range_diff = new_range[1]-new_range[0]
            
            for obj in list_object:
                diff = obj[feild] - old_range[0]
                obj[feild] = ((diff * new_range_diff) / old_range_diff) + new_range[0]
                
            return list_object
        
        except Exception as e:
            raise Exception(e)
    
    
    @check_size
    def get_searched_result(self, sentence: str, size: int=None, with_answer: bool=False, with_tag: bool=False)->List[object]:
        """
         return all matched questions sementics and keywords based

        Parameters
        ----------
        sentence : str
            sentence need to search.
        size : int
            size of output result list.
        with_answer : bool, optional
            response with answer included. The default is False.
        with_tag : bool, optional
            response with tag included. The default is False.

        Returns
        -------
        object
            DESCRIPTION.

        """
        try:
            # keyword based search
            keyword_search = self.keyword_search(sentence, "title",  self.constant['questionIndexName'])
            nn_search = self.cosine_similarity_search(sentence, "title_vector", self.constant['questionIndexName'])
            kw_hits,  nn_hits = [], []
            
            if keyword_search:
                kw_hits = keyword_search['hits']['hits']
                old_range = (0, keyword_search['hits']['max_score'])
                new_range = (0, 2)
                kw_hits = self._rescale(kw_hits, '_score', old_range, new_range)
                
            if nn_search:
                nn_hits = nn_search['hits']['hits']
            
            result, duplicate = [], {}
            i, j = 0, 0
            nkeyword, nnnsearch = len(kw_hits), len(nn_hits)
            
            limit = min(nkeyword+nnnsearch, size) if size else nkeyword+nnnsearch
            
            while i < nkeyword and j < nnnsearch:
                kwscore = kw_hits[i]['_score']
                kwobject = kw_hits[i]['_source']
                nnscore = nn_hits[j]['_score']
                nn_object = nn_hits[j]['_source']
                robj = None
                if kwscore > nnscore:
                    if kwobject['id'] not in duplicate:
                        robj = self._result_object(kwobject, kwscore, 'keywordScore',
                                                               with_answer, with_tag)
                    else:
                        result[duplicate[kwobject['id']]]['keywordScore'] = kwscore
                        
                    i += 1
                else:
                    if nn_object['id'] not in duplicate:
                        robj = self._result_object(nn_object, nnscore,'nnScore',
                                                           with_answer, with_tag)
                    else:
                        result[duplicate[nn_object['id']]]['nnScore'] = nnscore
                        
                    j += 1
                
                if robj:
                    duplicate[robj['id']] = len(result)
                    result.append(robj)
                
                if len(result) == limit:
                    return result
                    
            while i < nkeyword:
                kwscore = kw_hits[i]['_score']
                kwobject = kw_hits[i]['_source']
                robj = None
                if kwobject['id'] not in duplicate:
                    robj = self._result_object(kwobject, kwscore, 'keywordScore',
                                                           with_answer, with_tag)
                else:
                    result[duplicate[kwobject['id']]]['keywordScore'] = kwscore
                        
                i += 1
                if robj:
                    duplicate[robj['id']] = len(result)
                    result.append(robj)
                
                if len(result) == limit:
                    return result 
            
            while j < nnnsearch:
                nnscore = nn_hits[j]['_score']
                nn_object = nn_hits[j]['_source']
                robj = None
                if nn_object['id'] not in duplicate:
                    robj = self._result_object(nn_object, nnscore, 'nnScore',
                                                       with_answer, with_tag)
                else:
                    result[duplicate[nn_object['id']]]['nnScore'] = nnscore
                        
                j += 1
                if robj:
                    duplicate[robj['id']] = len(result)
                    result.append(robj)
                
                if len(result) == limit:
                    return result
                
            return result
        
        except Exception as e:
            raise Exception(e)
    
    
# End