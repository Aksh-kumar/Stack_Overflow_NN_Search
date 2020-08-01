# -*- coding: utf-8 -*-
import json
from urllib import parse, request

######## constant ###############
TIMEOUT = 5000

class APIRequest:
    """
    Used to fetch data from given API
    """
    
    def __init__(self):
        pass
    
    def get_header(self, contenttype: str, **kwargs)->object:
        """
        get headers with required configuration default json type header is returned
        params:
            contenttype (str): contenet type e.g. json, text e.t.c 
            **kwargs: axtra parameter to header
        return:
            header dictionary
        """
        headers = {
                'Content-Type': 'application/'+contenttype+'; charset=utf-8',
                'cache-control': 'no-cache'
                }  
        extra_args = locals()
        
        if extra_args:
            headers = {**headers, **kwargs}
        
        return headers

    
    def GET(self, url: str, header:dict=None)->object:
        """
        GET request data from given url
        parmas:
            url (str): url of API
            header(optional): dictionary of header parameters if not given json will be taken
        returns:
            JSON object of response
        """
        try:
            header = header if header is not None else self.get_header('json')
            req =  request.Request(url, headers=header, method='GET')
            
            with request.urlopen(req, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        
        except Exception as e:
           raise Exception(e)
            
            
    def POST(self, url: str, payload: object, header: dict=None) -> object:
        """
        POST request data from given url

        Parameters
        ----------
        url : str
            url of API.
        payload : object
            payload for post request must be serializable.
        header : dict, optional
            dictionary of header parameters if not given json will be taken
                              but content-type need to be x-www-form-urlencoded.
                              The default is None.

        Returns
        -------
        object
            JSON object of response.

        """
        try:
            header = header if header is not None else self.get_header('x-www-form-urlencoded')
            
            if header['Content-Type'].split(';')[0].split('/')[1] != 'json':
                payload = parse.urlencode(payload).encode()
            else:
                payload = payload.encode('utf-8')
            
            req =  request.Request(url, data=payload, headers=header, method='POST')
            
            with request.urlopen(req, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        
        except Exception as e:
            raise Exception(e)
    
    
    def PUT(self, url: str, payload: object, header: dict=None) -> object:
        """
        PUT request data from given url
        parmas:
            url (str): url of API
            payload (object): payload for put request 
            header(optional): dictionary of header parameters if not given json will be taken
                              but content-type need to be x-www-form-urlencoded
        returns:
            JSON object of response
        """
        try:
            header = header if header is not None else self.get_header('x-www-form-urlencoded')
            
            if header['Content-Type'].split(';')[0].split('/')[1] != 'json':
                payload = parse.urlencode(payload).encode()
            else:
                payload = payload.encode('utf-8')
            #data = parse.urlencode(payload).encode()
            req =  request.Request(url, data=payload, headers=header, method='PUT')
            
            with request.urlopen(req, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
            
        except Exception as e:
            raise Exception(e)


    def DELETE(self, url: str, _id: str, header: dict=None) -> object:
        """
        DELETE request data from given url
        parmas:
            url (str): url of API
            _id (str): id need to be deleted
            header(optional): dictionary of header parameters if not given json will be taken
        returns:
            JSON object of response
        """
        try:
            header = header if header is not None else self.get_header('x-www-form-urlencoded')
            req =  request.Request(url+'/'+str(_id), headers=header, method='DELETE')
            
            with request.urlopen(req, timeout=TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        
        except Exception as e:
            raise Exception(e)
    
    
#End
