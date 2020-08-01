# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

TIMEOUT_CONST = 30

class ElasticSearchConnection:
    """
    create connection to elastic search engine
    """
    
    def __init__(self)->None:
        """
        initializer method 
        """    
        self.conn_cache = {}    
    
    def get_conn_object(self, host: str, port: int, use_ssl:bool=False)->object:
        """
        create connection with elastic search serivice

        Parameters
        ----------
        host : str
            IP address of server which elastic search is running.
        port : int
            Post which elastic search service is Running.
        use_ssl : bool, optional
            whether to use ssl. The default is False.

        Raises
        ------
        Exception
            raise generic error if connection is not made.

        Returns
        -------
        object
            elastic search connction object.

        """
        try:
            if host+str(port) in self.conn_cache:
                return self.conn_cache[host+str(port)]
            
            es = Elasticsearch([{'host': host, 'port': port, 'use_ssl': use_ssl, 'timeout': TIMEOUT_CONST}])
            self.conn_cache[host+str(port)] = es
            
            if es.ping():
                return es 
            else:
                raise Exception("Elastic search connection not established")
        
        except Exception as e:
            raise Exception("some error occured while establish connection", e)
            
# End
