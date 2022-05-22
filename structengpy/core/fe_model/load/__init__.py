# -*- coding: utf-8 -*-
class LoadCase(object):
    def __init__(self,name:str):
        self.__name=name

    @property
    def name(self):
        return self.__name