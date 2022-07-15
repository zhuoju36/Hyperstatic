import numpy as np
from sympy import re     
from structengpy.core.fe_model.material.isotropy import IsotropicMaterial
class BeamSection(object):
    def __init__(self,name:str,material:IsotropicMaterial,shape:str,sizes,A,As2,As3,J,I22,I33,W22,W33):
        self.__name=name
        self.__material=material
        self.__shape=shape
        self.__A=A
        self.__As2=As2
        self.__As3=As3
        self.__J=J
        self.__I22=I22
        self.__I33=I33
        self.__W22=W22
        self.__W33=W33
        self.__shape='general'
        self.__sizes=sizes


    @property
    def name(self):
        return self.__name

    @property
    def material(self):
        return self.__material.name

    @property
    def rho(self):
        return self.__material.rho

    @property
    def E(self):
        return self.__material.E

    @property
    def mu(self):
        return self.__material.mu

    @property
    def G(self):
        return self.__material.G

    @property
    def i22(self):
        return (self.__I22/self.A)**0.5

    @property
    def i33(self):
        return (self.__I33/self.A)**0.5

    @property
    def lamda(self):
        return self.__material.rho*self.A

    @property
    def sizes(self):
        return tuple(self.__sizes)

    @property
    def shape(self):
        return self.__shape

    @property
    def A(self):
        return self.__A

    @property
    def As2(self):
        return self.__As2

    @property
    def As3(self):
        return self.__As3

    @property
    def J(self):
        return self.__J

    @property
    def I22(self):
        return self.__I22

    @property
    def I33(self):
        return self.__I33

    @property
    def W22(self):
        return self.__W22

    @property
    def W33(self):
        return self.__W33

    @property
    def i22(self):
        return (self.__I/self.__A)**0.5

    @property
    def i33(self):
        return (self.__I/self.__A)**0.5

class BoxSection(BeamSection):
    def __init__(self, name: str, material: IsotropicMaterial, h,b,tw,tf):
        A=h*b-(h-2*tf)*(b-2*tw)
        As2=2*tw*h
        As3=2*tf*b
        a=2*((b-tw)/tf+(h-tf)/tw)  
        Omega=2*(h-tf)*(b-tw)
        c=Omega/a
        J=c*Omega
        I22=h*b**3/12-(h-2*tf)*(b-2*tw)**3/12
        I33=b*h**3/12-(b-2*tw)*(h-2*tf)**3/12
        W22=I22/(b/2)
        W33=I33/(h/2)
        shape='box'
        sizes=[h,b,tw,tf]
        super().__init__(name, material, shape, sizes,A, As2, As3, J, I22, I33, W22, W33)

class PipeSection(BeamSection):
    def __init__(self, name: str, material: IsotropicMaterial, d,t):
        name=name
        material=material
        A=3.14159/4*(d**2-(d-2*t)**2)
        As2=As3=3.14159*t*(d-t)/2
        J=3.14159/32*(d**4-(d-2*t)**4)
        I22=I33=3.14159/64*(d**4-(d-2*t)**4)
        W22=I22/(d/2)
        W33=I33/(d/2)
        shape='pipe'
        sizes=[d,t]
        super().__init__(name, material, shape, sizes, A, As2, As3, J, I22, I33, W22, W33)

class ISection(BeamSection):
    def __init__(self,name,material,h,b,tw,tf):
        name=name
        material=material
        A=b*h-(b-tw)*(h-2*tf)
        As2=tw*h
        As3=5/3*tf*b 
        s=sum([np.tanh(m*3.141592*tf/2/b)/m**5 for m in range(1,30,2)])#翼缘取薄膜比拟前30阶
        beta=1/3-64*b/(3.141592**5*tf)*s        
        J=tf*b**3*beta*2
        s=sum([np.tanh(m*3.141592*tw/2/(h-2*tf))/m**5 for m in range(1,30,2)])#腹板取薄膜比拟前30阶
        beta=1/3-64*(h-2*tf)/(3.141592**5*tw)*s        
        J+=tw*(h-2*tf)**3*beta
        I22=1/12*tf*b**3*2+1/12*h*tw**3
        I33=(b*h**3-(b-tw)*(h-2*tf)**3)/12
        W22=I22/(b/2)
        W33=I33/(h/2)
        shape='I'
        sizes=[h,b,tw,tf]
        super().__init__(name, material, shape, sizes, A, As2, As3, J, I22, I33, W22, W33)

class CircleSection(BeamSection):
    def __init__(self,name,material,d):
        name=name
        material=material
        A=3.14159/4*d**2
        As2=As3=3.14159*d**2/4*0.9
        J=3.14159/32*d**4
        I22=I33=3.14159/64*d**4
        W22=I22/(d/2)
        W33=I33/(d/2)
        shape='circle'
        sizes=[d]
        super().__init__(name, material, shape, sizes, A, As2, As3, J, I22, I33, W22, W33)

class RectangleSection(BeamSection):
    def __init__(self,name,material,h,b):
        name=name
        material=material
        A=b*h
        As2=As3=5/6*h*b
        s=sum([np.tanh(m*3.141592*h/2/b)/m**5 for m in range(1,60,2)])#取薄膜比拟前60阶
        beta=1/3-64*b/(3.141592**5*h)*s        
        J=h*b**3*beta
        I22=h*b**3/12
        I33=b*h**3/12
        W22=I22/(b/2)
        W33=I33/(h/2)
        shape='R'
        sizes=[h,b]
        super().__init__(name, material, shape, sizes, A, As2, As3, J, I22, I33, W22, W33)

    # @classmethod
    # def create_C(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     name=name
    #     material=material
    #     A=b*h
    #     As2=As3=5/6*h*b
    #     J=h*b**3/3  #error
    #     I22=h*b**3/12
    #     I33=b*h**3/12
    #     shape='C'
    #     return ins    

    # @classmethod
    # def create_Z(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     name=name
    #     material=material
    #     A=b*h
    #     As2=As3=5/6*h*b
    #     J=h*b**3/3  #error
    #     I22=h*b**3/12
    #     I33=b*h**3/12
    #     shape='Z'
    #     return ins

    # @classmethod
    # def create_L(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     name=name
    #     material=material
    #     A=b*h
    #     As2=As3=5/6*h*b
    #     J=h*b**3/3  #error
    #     I22=h*b**3/12
    #     I33=b*h**3/12
    #     shape='L'
    #     return ins  

    # @classmethod
    # def create_quad(cls,name,material,pt1,pt2,pt3,pt4,t1,t2,t3,t4):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     name=name
    #     material=material
    #     A=
    #     As2=
    #     As3=
    #     J=
    #     I22=
    #     I33=
    #     shape='quad'
    #     return ins
if __name__=='__main__':
    box=BoxSection('box',None,400,200,14,20)
    assert box.A==18080
    assert 2.742e8*0.99<=box.J<=2.742e8*1.01 #J error
    assert 3.979e8*0.99<=box.I33<=3.979e8*1.01
    assert 1.140e8*0.99<=box.I22<=1.140e8*1.01
    assert box.As2==11200
    assert box.As3==8000
    
    pipe=PipeSection('pipe',None,400,20)
    assert 23876.104*0.99<= pipe.A<=23876.104*1.01
    assert 8.643e8*0.99<=pipe.J<=8.643e8*1.01
    assert 4.322e8*0.99<=pipe.I33<=4.322e8*1.01
    assert 4.322e8*0.99<=pipe.I22<=4.322e8*1.01
    assert 11960.078*0.99<=pipe.As2<=11960.078*1.01
    assert 11960.078*0.99<=pipe.As3<=11960.078*1.01
    
    Isection=ISection('Isection',None,400,200,14,20)
    assert 13040*0.99<=Isection.A<=13040*1.01
    print("Isection.J: "+str(Isection.J))
    # assert 1320679.3*0.99<=Isection.J<=1320679.3*1.01
    assert 3.435e8*0.99<=Isection.I33<=3.435e8*1.01
    assert 26748987*0.99<=Isection.I22<=26748987*1.01
    assert 5600*0.99<=Isection.As2<=5600*1.01
    assert 6666.6667*0.99<=Isection.As3<=6666.6667*1.01
    
    circle=CircleSection('circle',None,400)
    assert 125663.71*0.99<=circle.A<=125663.71*1.01
    assert 2.513e9*0.99<=circle.J<=2.513e9*1.01
    assert 1.257e9*0.99<=circle.I33<=1.257e9*1.01
    assert 1.257e9*0.99<=circle.I22<=1.257e9*1.01
    assert 113097.34*0.99<=circle.As2<=113097.34*1.01
    assert 113097.34*0.99<=circle.As3<=113097.34*1.01
    
    rectangle=RectangleSection('rectangle',None,400,200)
    assert 80000*0.99<=rectangle.A<=80000*1.01
    assert 7.324e8*0.99<=rectangle.J<=7.324e8*1.01 #error
    assert 1.067e9*0.99<=rectangle.I33<=1.067e9*1.01
    assert 2.667e8*0.99<=rectangle.I22<=2.667e8*1.01
    assert 66666.67*0.99<=rectangle.As2<=66666.67*1.01
    assert 66666.67*0.99<=rectangle.As3<=66666.67*1.01
    
    sec=PipeSection('name',None,245,8)
    W=sec.I22/(245/2)
    sigma=20e3*6000/4/W
    print(sigma)