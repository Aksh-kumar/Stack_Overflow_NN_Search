# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 22:47:34 2020

@author: Akash Kumar
"""

## importing necessary module

import tensorflow as tf
import tensorflow_hub as hub
from typing import List

########## constants ########################
#constant model path
USE_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"

class EmbeddingModel:
    """
    create different types of embedding model
    """
       
    def __init__(self, **kwargs):
        """
        Initialize method

        Parameters
        ----------
        **kwargs : TYPE
            dictionary of model name to model path mapping.

        Returns
        -------
        None.

        """    
        self.model_cache = {}
        if 'USE' in kwargs:
            
            self.USE(kwargs['USE'])
        
    
    
    def USE(self, model_path: str=None)-> object :
        """
        get Universal Sentence Encoder's model

        Parameters
        ----------
        model_path : str, optional
            model path if saved locally. The default is None.

        Raises
        ------
        Exception
            raise Exception if path or model is not found.

        Returns
        -------
        object 
            tensorflow model.

        """
        try:                
            if model_path is not None:
                model = hub.load(hub.resolve(model_path))
                self.model_cache['USE'] = model
                return model
            
            if 'USE' in self.model_cache:
                return self.model_cache['USE']            
            
            self.model_cache['USE'] = hub.load(USE_URL)
            return self.model_cache['USE']
        
        except Exception as e:
            raise Exception("some error occured while loading model", e)
        
    
# End

class WordEmbedding:
    """
    Create sentence vector By using Embedding Models
    """
      
    def __init__(self, model: EmbeddingModel)-> None:
        """
        initialize funtion

        Parameters
        ----------
        model : EmbeddingModel
            EmbeddingModel object.

        Returns
        -------
        None

        """
        self.model = model
        
    
    def getEmbedding_vector(self, sentence: List[str], model_name: str='USE')->List[List[float]]:
        """
        convert sentence string to vector

        Parameters
        ----------
        sentence : List[str]
            sentence list.
        model_name : str, optional
            name of model need to use. The default is 'USE'.

        Raises
        ------
        Exception
            raise generic Exception if some eror occured.

        Returns
        -------
        List[List[float]]
            word enbedding vector.

        """
        try:
            if model_name == 'USE':
                model = self.model.USE()
                vec = model(sentence)
                res = tf.make_ndarray(tf.make_tensor_proto(vec)).tolist()
                #print(res)
                return res
            else:
                raise Exception("Model Not found")
        
        except Exception as e:
            raise Exception("model not found", e)

#End
#if __name__ == '__main__':
#path = os.path.join(os.getcwd(), 'USEModel')
#emb_model = EmbeddingModel(USE= path)
#word_embedding = WordEmbedding(emb_model)
#vec = word_embedding.getEmbedding_vector(['my name is akash'])
#print(vec)
    
