# -*- coding: utf-8 -*-
class LoadCase(object):
    def __init__(self,name:str):
        self.__name=name
        self.__hid

    @property
    def name(self):
        return self.__name

    @property
    def hid(self):
        return self.__hid

    @hid.setter
    def hid(self,val):
        assert type(val)==int
        self.__hid=val