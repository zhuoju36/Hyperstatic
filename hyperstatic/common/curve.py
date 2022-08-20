
from os import curdir
import numpy as np

class Curve(object):
    def __init__(self,name:str,x:list,y:list):
        self.__name=name
        self.__x=np.array(x,dtype=float)
        self.__y=np.array(y,dtype=float)

    @property
    def name(self):
        return self.__name

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def to_array(self):
        return np.vstack([self.__x,self.__y])

    @staticmethod
    def sin(name:str,A:float,w:float,phi:float,dt:float,n:int):
        x=np.arange(0,n*dt,dt)
        y=A*np.sin(w*x+phi)
        return Curve(name,x,y)

    @staticmethod
    def cos(name:str,A:float,w:float,phi:float,dt:float,n:int):
        x=np.arange(0,n*dt,dt)
        y=A*np.cos(w*x+phi)
        return Curve(name,x,y)