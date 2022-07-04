
import numpy as np

class Curve(object):
    def __init__(self,name:str,x:list,y:list):
        self.__name=name
        self.__x=np.array(x)
        self.__y=np.array(y)

    @property
    def name(self):
        return self.__name

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @classmethod
    def from_file(cls,self):
        pass

    @classmethod
    def from_function(cls,func):
        pass