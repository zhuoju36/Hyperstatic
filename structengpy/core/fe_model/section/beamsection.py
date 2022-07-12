import numpy as np
if __name__ == '__main__':
    import sys
    sys.path.append('.')
    from thinwall import QuadThinWall
else:
    from .thinwall import QuadThinWall 
     
class BeamSection():
    def __init__(self,name,material,A,As2,As3,J,I22,I33,W22,W33):
        self.name=name
        self.material=material
        self.A=A
        self.As2=As2
        self.As3=As3
        self.J=J
        self.I22=I22
        self.I33=I33
        self.W22=W22
        self.W33=W33
        self.shape='G'
        self.sizes=[]

    @property
    def E(self):
        return self.material.E

    @property
    def G(self):
        return self.material.G

    @property
    def i22(self):
        return (self.I22/self.A)**0.5

    @property
    def i33(self):
        return (self.I33/self.A)**0.5

    @property
    def lamb(self):
        return self.material.gamma*self.A

    @classmethod
    def create_box(cls,name,material,h,b,tw,tf):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        ins.A=h*b-(h-2*tf)*(b-2*tw)
        ins.As2=2*tw*h
        ins.As3=2*tf*b
        a=2*((b-tw)/tf+(h-tf)/tw)  
        Omega=2*(h-tf)*(b-tw)
        c=Omega/a
        ins.J=c*Omega
        ins.I22=h*b**3/12-(h-2*tf)*(b-2*tw)**3/12
        ins.I33=b*h**3/12-(b-2*tw)*(h-2*tf)**3/12
        ins.W22=ins.I22/(b/2)
        ins.W33=ins.I33/(h/2)
        ins.shape='B'
        ins.sizes=[h,b,tw,tf]
        return ins

    @classmethod
    def create_pipe(cls,name,material,d,t):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        ins.A=3.14159/4*(d**2-(d-2*t)**2)
        ins.As2=ins.As3=3.14159*t*(d-t)/2
        ins.J=3.14159/32*(d**4-(d-2*t)**4)
        ins.I22=ins.I33=3.14159/64*(d**4-(d-2*t)**4)
        ins.W22=ins.I22/(d/2)
        ins.W33=ins.I33/(d/2)
        ins.shape='O'
        ins.sizes=[d,t]
        return ins

    @classmethod
    def create_Isection(cls,name,material,h,b,tw,tf):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        ins.A=b*h-(b-tw)*(h-2*tf)
        ins.As2=tw*h
        ins.As3=5/3*tf*b 
        s=sum([np.tanh(m*3.141592*tf/2/b)/m**5 for m in range(1,30,2)])#翼缘取薄膜比拟前30阶
        beta=1/3-64*b/(3.141592**5*tf)*s        
        ins.J=tf*b**3*beta*2
        s=sum([np.tanh(m*3.141592*tw/2/(h-2*tf))/m**5 for m in range(1,30,2)])#腹板取薄膜比拟前30阶
        beta=1/3-64*(h-2*tf)/(3.141592**5*tw)*s        
        ins.J+=tw*(h-2*tf)**3*beta

        ins.I22=1/12*tf*b**3*2+1/12*h*tw**3
        ins.I33=(b*h**3-(b-tw)*(h-2*tf)**3)/12
        ins.W22=ins.I22/(b/2)
        ins.W33=ins.I33/(h/2)
        ins.shape='I'
        ins.sizes=[h,b,tw,tf]
        return ins

    @classmethod
    def create_circle(cls,name,material,d):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        ins.A=3.14159/4*d**2
        ins.As2=ins.As3=3.14159*d**2/4*0.9
        ins.J=3.14159/32*d**4
        ins.I22=ins.I33=3.14159/64*d**4
        ins.W22=ins.I22/(d/2)
        ins.W33=ins.I33/(d/2)
        ins.shape='o'
        ins.sizes=[d]
        return ins

    @classmethod
    def create_rectangle(cls,name,material,h,b):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        ins.A=b*h
        ins.As2=ins.As3=5/6*h*b
        s=sum([np.tanh(m*3.141592*h/2/b)/m**5 for m in range(1,60,2)])#取薄膜比拟前60阶
        beta=1/3-64*b/(3.141592**5*h)*s        
        ins.J=h*b**3*beta
        ins.I22=h*b**3/12
        ins.I33=b*h**3/12
        ins.W22=ins.I22/(b/2)
        ins.W33=ins.I33/(h/2)
        ins.shape='R'
        ins.sizes=[h,b]
        return ins

    @classmethod
    def create_quad(cls,name,material,pt1,pt2,pt3,pt4,t12,t23,t34,t41):
        ins=super(BeamSection,cls).__new__(cls)
        ins.name=name
        ins.material=material
        (x1,y1)=pt1
        (x2,y2)=pt2
        (x3,y3)=pt3
        (x4,y4)=pt4
        qtw=QuadThinWall(x1,y1,x2,y2,x3,y3,x4,y4,t12,t23,t34,t41)
        ins.A=qtw.A
        ins.As2=ins.As3=0.5*qtw.A
        ins.J=qtw.J
        ins.I22=qtw.I22
        ins.I33=qtw.I33
        ins.W22=ins.I22/max(abs(x1),abs(x2),abs(x3),abs(x4))
        ins.W33=ins.I33/max(abs(y1),abs(y2),abs(y3),abs(y4))
        ins.shape='Q'
        ins.sizes=[x1,y1,x2,y2,x3,y3,x4,y4,t12,t23,t34,t41]
        return ins
        

    # @classmethod
    # def create_C(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     ins.name=name
    #     ins.material=material
    #     ins.A=b*h
    #     ins.As2=ins.As3=5/6*h*b
    #     ins.J=h*b**3/3  #error
    #     ins.I22=h*b**3/12
    #     ins.I33=b*h**3/12
    #     ins.shape='C'
    #     return ins    

    # @classmethod
    # def create_Z(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     ins.name=name
    #     ins.material=material
    #     ins.A=b*h
    #     ins.As2=ins.As3=5/6*h*b
    #     ins.J=h*b**3/3  #error
    #     ins.I22=h*b**3/12
    #     ins.I33=b*h**3/12
    #     ins.shape='Z'
    #     return ins

    # @classmethod
    # def create_L(cls,name,material,h,b):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     ins.name=name
    #     ins.material=material
    #     ins.A=b*h
    #     ins.As2=ins.As3=5/6*h*b
    #     ins.J=h*b**3/3  #error
    #     ins.I22=h*b**3/12
    #     ins.I33=b*h**3/12
    #     ins.shape='L'
    #     return ins  

    # @classmethod
    # def create_quad(cls,name,material,pt1,pt2,pt3,pt4,t1,t2,t3,t4):
    #     ins=super(BeamSection,cls).__new__(cls)
    #     ins.name=name
    #     ins.material=material
    #     ins.A=
    #     ins.As2=
    #     ins.As3=
    #     ins.J=
    #     ins.I22=
    #     ins.I33=
    #     ins.shape='quad'
    #     return ins

if __name__=='__main__':
    box=BeamSection.create_box('box',None,400,200,14,20)
    assert box.A==18080
    assert 2.742e8*0.99<=box.J<=2.742e8*1.01 #J error
    assert 3.979e8*0.99<=box.I33<=3.979e8*1.01
    assert 1.140e8*0.99<=box.I22<=1.140e8*1.01
    assert box.As2==11200
    assert box.As3==8000
    
if __name__=='__main__':
    pipe=BeamSection.create_pipe('pipe',None,400,20)
    assert 23876.104*0.99<= pipe.A<=23876.104*1.01
    assert 8.643e8*0.99<=pipe.J<=8.643e8*1.01
    assert 4.322e8*0.99<=pipe.I33<=4.322e8*1.01
    assert 4.322e8*0.99<=pipe.I22<=4.322e8*1.01
    assert 11960.078*0.99<=pipe.As2<=11960.078*1.01
    assert 11960.078*0.99<=pipe.As3<=11960.078*1.01
    
if __name__=='__main__':
    Isection=BeamSection.create_Isection('Isection',None,400,200,14,20)
    assert 13040*0.99<=Isection.A<=13040*1.01
    print("Isection.J: "+str(Isection.J))
    # assert 1320679.3*0.99<=Isection.J<=1320679.3*1.01
    assert 3.435e8*0.99<=Isection.I33<=3.435e8*1.01
    assert 26748987*0.99<=Isection.I22<=26748987*1.01
    assert 5600*0.99<=Isection.As2<=5600*1.01
    assert 6666.6667*0.99<=Isection.As3<=6666.6667*1.01
    
if __name__=='__main__':
    circle=BeamSection.create_circle('circle',None,400)
    assert 125663.71*0.99<=circle.A<=125663.71*1.01
    assert 2.513e9*0.99<=circle.J<=2.513e9*1.01
    assert 1.257e9*0.99<=circle.I33<=1.257e9*1.01
    assert 1.257e9*0.99<=circle.I22<=1.257e9*1.01
    assert 113097.34*0.99<=circle.As2<=113097.34*1.01
    assert 113097.34*0.99<=circle.As3<=113097.34*1.01
    
if __name__=='__main__':
    rectangle=BeamSection.create_rectangle('rectangle',None,400,200)
    assert 80000*0.99<=rectangle.A<=80000*1.01
    assert 7.324e8*0.99<=rectangle.J<=7.324e8*1.01 #error
    assert 1.067e9*0.99<=rectangle.I33<=1.067e9*1.01
    assert 2.667e8*0.99<=rectangle.I22<=2.667e8*1.01
    assert 66666.67*0.99<=rectangle.As2<=66666.67*1.01
    assert 66666.67*0.99<=rectangle.As3<=66666.67*1.01
    
if __name__=='__main__':
    sec=BeamSection.create_pipe('name',None,245,8)
    W=sec.I22/(245/2)
    sigma=20e3*6000/4/W
    print(sigma)