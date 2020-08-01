# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:57:22 2020

@author: Akash Kumar
"""

#importing libraries
import json
import csv
import os
import math
from enum import Enum
from datetime import datetime as dt
from typing import List, TypeVar
from elasticsearch import helpers

StrList = TypeVar('StrList', str, List[str])

################## constants #######################

QUESTION_MAPPING = None
ANSWER_MAPPING = None
TAG_MAPPING = None
QUESTION_INDEX_NAME = None
ANSWER_INDEX_NAME = None
TAG_INDEX_NAME = None
QUESTION_CSV = None
ANSWER_CSV = None
TAG_CSV = None
DATE_NULL_VALUE = None
OWNERID_NULL_VALUE = None
CHUNK_SIZE = None
TOTAL_QUESTION_COUNT = None

class CSVType(Enum):
    QUESTION = 1,
    ANSWER = 2,
    TAG = 3
# End


class CreateIndex:
    """
    create Data Index in elastic search
    """
    
    def __init__(self, esobj: object, **kwargs) -> None:
        """

        Parameters
        ----------
        esobj : object
            (ElasticSearch):Elastic Search  object.
        **kwargs : TYPE
            Extra Argument provided.

        Raises
        ------
        None

        Returns
        -------
        None

        """
        ## https://www.kaggle.com/stackoverflow/stacksample data
        """
        Questions:- contains the title, body, creation date, closed date (if applicable),
        score, and owner ID for all non-deleted Stack Overflow questions whose Id is a 
        multiple of 10.
        Answers:- contains the body, creation date, score, and owner ID for each of the 
        answers to these questions. The ParentId column links back to the Questions table.
        Tags:- contains the tags on each of these questions
        """
        if(esobj is None):
            raise Exception("Elastic search connection object not found")
        
        self.word_embedding = None
        if 'embedding_model' in kwargs:
            self.word_embedding = kwargs['embedding_model']
        
        self.esobj = esobj
        self.question_column = ['id', 'ownerUserId', 'creationDate', 'closedDate', 'score', 'title', 'body', 'title_vector']
        self.answer_column = ['id', 'ownerUserId' , 'creationDate', 'parentId', 'score', 'body']
        self.tag_column = ['id', 'questionId', 'tag']
    
    
    def get_date(self, date_str: str)-> object:
        """
        convert date to given format if not then return None
        
        Parameters
        ----------
        date_str : str
            date in string format (str).

        Returns
        -------
        object
            Datetime object.

        Error:
        -------
            ValueError
        """
        try:
            DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"        
            return dt.strptime(date_str, DATE_TIME_FORMAT)
        except ValueError as e:
            raise Exception(e)
    
    
    def _create_index(self, indexname: StrList, b: str)-> bool:
        """
        create Index in elastic search db

        Parameters
        ----------
        indexname : StrList
            name or list of names of index need to be created.
        b : str
             mapping configuration body 

        Returns
        -------
        bool
            whether index is created or already present or some error occured..

        """
        try:
            if isinstance(indexname, str):
                indexname = [indexname]
            
            res = []
            for indexes in indexname:
                
                response = self.esobj.indices.create(index= indexes, ignore=400, body=b) #400 caused by IndexAlreadyExistsException,     
                if 'acknowledged' in response:
                    if response['acknowledged'] == True:
                        print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])
                        res.append(True)
                # catch API error response
                elif 'error' in response:
                    #print("status "+ str(response['status']))
                    res.append(False if response['status'] != 400 else True)
            
            return all(res)
        except Exception as e:
            raise Exception(e)
    
    
    def check_index_exists(self, indexes: StrList)->bool:
        """
        check Index created or not

        Parameters
        ----------
        indexes : StrList
            indexes list or string.

        Returns
        -------
        bool
            present or not.

        """
        if isinstance(indexes, str):
            return self.esobj.indices.exists(index=indexes)
        
        if isinstance(indexes, list):
            
            res = []
            for _index in indexes:
                res.append(self.esobj.indices.exists(index=_index))
            
            return all(res)
        
        return False
    
    def _get_mapping(self, jsonpath: str)->object:
        """
        geto JSON from Json file

        Parameters
        ----------
        jsonpath : str
            json file path.

        Returns
        -------
        object
            Json object.

        """
        try:
            with open(jsonpath) as f:
                return json.load(f)
        
        except Exception as e:
            raise Exception(e)
    
    
    def _get_bulk_insert_object(self, mapping: dict, indexname: str,_id: int, _type: str='_doc')->object:
        """
        get bulk insertion object

        Parameters
        ----------
        mapping : dict
            data need to be inserted.
        indexname : str
            name of index.
        _id : int
            data id.
        _type : str, optional
            type feild in index. The default is '_doc'.

        Returns
        -------
        object
            required object for bulk insertion.

        """
        return { "_index": indexname, "_type": _type, "_id": _id, "_source": mapping }
    
    
    def _bulk_insert(self, data: List[object])->bool:
        """
        insert list of data in bulk
        
        Parameters
        ----------
        data : List[object]
            Iterable of data (list).

        Raises
        ------
        Exception
            Generic exception if not inserted.

        Returns
        -------
        bool
            whether sucessfully inserted or not.

        """
        
        try:
            ok, err = helpers.bulk(self.esobj, data, request_timeout=60)
            if err:
                msg =  "Error during upload. %s documents successfully uploaded. \
                        Message: %s.\n"
                raise Exception(msg % (ok, "\n".join(err)))
            
            return True
        
        except Exception as e:
            raise Exception(e)
    
    
    def _delete_index(self, index_name: str, verbose:bool=False)->bool:
        """
        delete indexes from elastic search db
        
        Parameters
        ----------
        index_name : str
            name of index which need to delete.
        verbose : bool, optional
            if true Print the output response after deletion. The default is False.

        Returns
        -------
        bool
            whether it is deleted or not.

        """
        try:
            
            res=self.esobj.indices.delete(index=index_name, ignore=[400, 404])
            if verbose:
                print(res)
            return True
        
        except Exception as e:
            raise Exception(e)
    
    
    def _insert_helper(self, data: List[object], verbose: bool=False)->bool:
        """
        helper method to bulk insert 
                  
        Parameters
        ----------
        data : List[object]
            data need to be bulk inserted.
        verbose : bool, optional
            display success message. The default is False.

        Returns
        -------
        bool
            success or failure.

        """
        first = data[0]['_id']
        last = data[-1]['_id']
        #insert data to API
        res = self._bulk_insert(data)
        if res and verbose:
            print("successfully inserted")
            print('first record', first)
            print('last record', last)
            return True
        
        return False
        
    
    def insert_data_to_index(self, datapath: str, csvtype: CSVType,
                                   index_name: StrList, id_index: int, totalcount: int=None)->bool:
        """
        Used to insert data to index by reading csv file
        
        Parameters
        ----------
        datapath : str
            csv file path need to read and dump into indexes.
        csvtype : CSVType
            type of csv Quesstion, answer or tag (ENUM CSVType).
        indexname : str
            name of index where data to be inserted.
        id_index : int
            id column index which is used as ID in document.
        totalcount: int
            number of documents available in the index
            used when data is distributed into multiple indexes
        
        Returns
        -------
        bool
            whether sucessfully inserted or not.

        """
        temp = []
        index, indexname, ismultiindex, parts = 0, None, False, None
        
        if isinstance(index_name, str):
            indexname = index_name
        
        if isinstance(index_name, list):
            indexname = index_name[index]
            ismultiindex = True
            
            if totalcount is None:
                raise Exception("totalcount value is not provided")
            
            parts = int(math.ceil(totalcount/len(index_name)))
        
        try:
            with open(datapath, encoding='latin1') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                _ = next(readCSV, None) # skip header
                count = 1
                
                for row in readCSV:
                    
                    if ismultiindex and index != count//parts:
                        index = count//parts
                        indexname = index_name[index]                    
                    
                    res = None
                    if csvtype == CSVType.QUESTION:
                        title_vector = self.word_embedding.getEmbedding_vector([row[5]])[0] if self.word_embedding is not None else [0]*512
                        row[3] = row[3] if row[3] != 'NA' else DATE_NULL_VALUE
                        row[1] = row[1] if row[1] != 'NA' else OWNERID_NULL_VALUE
                        values = [int(row[0]), int(row[1]), row[2], row[3],
                                  int(row[4]), row[5], row[6], title_vector]
                        
                        mapping = dict(zip(self.question_column, values))
                        
                        temp.append(self._get_bulk_insert_object(mapping, indexname, values[id_index]))
                        #res = self.esobj.index(index=indexname, id=values[id_index], body=mapping)
                        
                    if csvtype == CSVType.ANSWER:
                        row[2] = row[2] if row[2] != 'NA' else DATE_NULL_VALUE
                        row[1] = row[1] if row[1] != 'NA' else OWNERID_NULL_VALUE
                        values = [int(row[0]), int(row[1]), row[2],
                                  int(row[3]), int(row[4]), row[5]]
                        
                        mapping = dict(zip(self.answer_column, values))
                        temp.append(self._get_bulk_insert_object(mapping, indexname, values[id_index]))
                        #res = self.esobj.index(index=indexname, id=values[id_index], body=mapping)    
                    
                    if csvtype == CSVType.TAG:
                        values = [count, int(row[0]), row[1]]
                        
                        mapping = dict(zip(self.tag_column, values))
                        temp.append(self._get_bulk_insert_object(mapping, indexname, values[id_index]))
                        #res = self.esobj.index(index=indexname, id=values[id_index], body=jsonformat)
                    
                    if len(temp) == CHUNK_SIZE:
                        res = self._insert_helper(temp, True)
                        if res:
                            print(str(count-400)+" to "+ str(count))
                            temp=[]
                        else:
                            assert False
                    count += 1
            
            if len(temp) > 0:
                res = self._insert_helper(temp, True)
                if res:
                    print(str(count-len(temp))+" to "+ str(count))
                
            return True
        except Exception as e:
            raise Exception(e)
    
    
    def index_csv(self)->bool:
        """
         driver method to index data 
        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        bool
            if successfully indexed into databases else false.

        """
        try:
            
            check = [QUESTION_MAPPING, ANSWER_MAPPING, TAG_MAPPING, QUESTION_CSV, ANSWER_CSV, TAG_CSV]
            not_exists = []
            
            for file_path in check:
                if not os.path.exists(file_path):
                    not_exists.append(file_path)
            
            if not_exists != []:
                raise Exception(' '.join(x for x in not_exists)+ ' file(s) are not exists')
            
            res = [False, False, False]
            
            if self.check_index_exists(indexes=QUESTION_INDEX_NAME):
                print("{0} index is already present skipping entry...".format(QUESTION_INDEX_NAME))
                res[0] = True
            else:
                if self._create_index(QUESTION_INDEX_NAME, self._get_mapping(QUESTION_MAPPING)):
                    res[0] = self.insert_data_to_index(QUESTION_CSV, CSVType.QUESTION,
                                                       QUESTION_INDEX_NAME, 0,
                                                       TOTAL_QUESTION_COUNT)
            
                        
            if self.check_index_exists(indexes=ANSWER_INDEX_NAME):
                print("{0} index is already present skipping entry...".format(ANSWER_INDEX_NAME))
                res[1] = True
            else:
                if self._create_index(ANSWER_INDEX_NAME, self._get_mapping(ANSWER_MAPPING)):
                    res[1] =  self.insert_data_to_index(ANSWER_CSV, CSVType.ANSWER, ANSWER_INDEX_NAME, 0)
        
            
            if self.check_index_exists(indexes=TAG_INDEX_NAME):
                print("{0} index is already present skipping entry...".format(TAG_INDEX_NAME))
                res[2] = True
            else:
                if self._create_index(TAG_INDEX_NAME, self._get_mapping(TAG_MAPPING)):
                    res[2] = self.insert_data_to_index(TAG_CSV, CSVType.TAG, TAG_INDEX_NAME, 0)
        
        
            return all(res)
    
        except Exception as e:
             raise Exception(e)
        
    
#End
            
def set_constant_file_path(constantJSON: dict)->None:
    """
    Parameters
    ----------
    constantJSON : dict
         configuration json

    Raises
    ------
    Exception
        Generic exception in data parsing.

    Returns
    -------
    None

    """
    try:
        global QUESTION_MAPPING, ANSWER_MAPPING, TAG_MAPPING, QUESTION_INDEX_NAME
        global ANSWER_INDEX_NAME, TAG_INDEX_NAME, QUESTION_CSV, ANSWER_CSV, TAG_CSV
        global DATE_NULL_VALUE, OWNERID_NULL_VALUE, CHUNK_SIZE, TOTAL_QUESTION_COUNT
        
        const = constantJSON
        QUESTION_MAPPING = os.path.abspath(const['questionMapping'])
        ANSWER_MAPPING = os.path.abspath(const['answerMapping'])
        TAG_MAPPING = os.path.abspath(const['tagMapping'])
        QUESTION_INDEX_NAME = const['questionIndexName']
        ANSWER_INDEX_NAME = const['answerIndexName']
        TAG_INDEX_NAME = const['tagIndexName']
        QUESTION_CSV = os.path.abspath(const['questionCSV'])
        ANSWER_CSV = os.path.abspath(const['answerCSV'])
        TAG_CSV = os.path.abspath(const['tagCSV'])
        DATE_NULL_VALUE = const['dateNULLValue']
        OWNERID_NULL_VALUE = int(const['ownerIDNULLValue'])
        CHUNK_SIZE = int(const['chunkSize'])
        TOTAL_QUESTION_COUNT = int(const['totalQuestionCount'])
        
    except KeyError as ke:
        raise Exception("invalid key please provide valid key")
    
    except Exception as e:
        raise Exception("some error occured while parsing constant json file")
#End


# Driver function to load data into elastic search db
def load_index_data(constantJSON: dict, esconn: object, word_embedding: object=None, force: bool=False)->bool:
    """
    Driver methd for indexing data from csv file to elastic search DB
    Parameters
    ----------
    constantJSON : dict
        all required constant json.
    esconn : object
        elastic search connection object
    word_embedding : object
        word embedding model connection model(default is None)
    
    Returns
    -------
    bool
       boolean whether all data is indexed or not.
    """
    set_constant_file_path(constantJSON)
    
    if word_embedding is None and not force:
        return False
    
    ci = CreateIndex(esconn, embedding_model=word_embedding)
    res = ci.index_csv()
    return res
#End

        
        
        
        