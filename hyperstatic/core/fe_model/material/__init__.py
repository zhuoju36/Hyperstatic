class Material(object):
    def __init__(self,name:str,rho:float,mat_model:str):
        self.__name=name 
        self.__rho=rho #density
        self.__mat_model=mat_model #material model

    @property
    def name(self):
        return self.__name

    @property
    def rho(self):
        return self.__rho

    @property
    def mat_model(self):
        return self.__mat_model

    @property
    def C(self):
        raise NotImplementedError

    @property
    def D(self):
        raise NotImplementedError