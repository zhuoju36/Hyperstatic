# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:21:57 2017

@author: zhuoj
"""
class Load(object):
    def __init__(self,lc):
        self._lc=lc
        
    @property
    def lc(self):
        return self._lc
    
    @lc.setter
    def lc(self,lc):
        self._lc=lc
        
class LoadPt(Load):
    def __init__(self,lc,targets,values):
        self._values=values
        super(Load,self).__init__(lc,targets)
    
    @property
    def values(self):
        return self._values
    
    @values.setter
    def values(self,val):
        assert len(val)==6
        self._values=val

class LoadFrmPt(Load):
    def __init__(self,lc,targets,values,loc):
        self._values=values
        self._loc=loc
        super(Load,self).__init__(lc,targets)
    @property
    def values(self):
        return self._values
    
    @values.setter
    def values(self,val):
        assert len(val)==6
        self._values=val
        
    @property
    def loc(self):
        return self._loc
    
    @loc.setter
    def loc(self,loc):
        assert (loc<=1 and loc>=0)
        self._loc=loc

class LoadFrmDistrib(Load):
    def __init__(self,lc,targets,values_i,values_j):
        self._values_i=values_i
        self._values_j=values_j
        super(Load,self).__init__(lc,targets)
        
    @property
    def values_i(self):
        return self.__values_i
    @values_i.setter
    def values_i(self,val):
        assert len(val)==6
        self._values_i=val
    
    @property
    def values_j(self):
        return self.__values_j
    @values_j.setter
    def values_j(self,val):
        assert len(val)==6
        self._values_j=val

class LoadFrmStrain(Load):
    def __init__(self,lc,targets,value):
        self._value=value
        super(Load,self).__init__(lc,targets)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self,val):
        assert type(val)==float and val<1
        self._values=val

class LoadFrmTmpt(Load):
    def __init__(self,lc,targets,value):
        self._value=value
        super(Load,self).__init__(lc,targets)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self,val):
        assert type(val)==float and val<1
        self._values=val

#class LoadAreaDistrib(load):
#    def __init__(self,lc,targets,values_1,values_2,values_3,values4):
#        pass
#        super(Load,self).__init__(lc,targets)
#        
#class LoadArea2Frame(load):
#    def __init__(self,lc,targets,values_1,values_2,values_3,values4):
#        pass
#        super(Load,self).__init__(lc,targets)

