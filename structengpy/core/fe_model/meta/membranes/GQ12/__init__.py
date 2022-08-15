import logging
import os
import sys

import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from structengpy.core.fe_model.meta.interpolate import Lagrange
from structengpy.core.fe_model.meta.jacobi import J2D
from structengpy.core.fe_model.meta.operator import L2,operator_dot
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,x4,y4,E,mu,t,xi,eta

xi0=[1,1,-1,-1]
eta0=[-1,1,1,-1]
x0=[x1,x2,x3,x4]
y0=[y1,y2,y3,y4]
N0=[]
Nut=[]
Nvt=[]

a1=sum([xi0[i]*x0[i] for i in range(4)])/4
a2=sum([eta0[i]*x0[i] for i in range(4)])/4
a3=sum([xi0[i]*eta0[i]*x0[i] for i in range(4)])/4
b1=sum([xi0[i]*y0[i] for i in range(4)])/4
b2=sum([eta0[i]*y0[i] for i in range(4)])/4
b3=sum([xi0[i]*eta0[i]*y0[i]  for i in range(4)])/4

for i in range(4):  
    N0.append(0.25*(1+xi0[i]*xi)*(1+eta0[i]*eta))    
    Nut.append((xi*(1-xi**2)*(b1+b3*eta0[i])*(1+eta0[i]*eta)+eta0[i]*(1-eta**2)*(b2+b3*xi0[i])*(1+xi0[i]*xi))/8)
    Nvt.append(-(xi*(1-xi**2)*(a1+a3*eta0[i])*(1+eta0[i]*eta)+eta0[i]*(1-eta**2)*(a2+a3*xi0[i])*(1+xi0[i]*xi))/8)
    
N=syp.zeros(2,3*4)
for i in range(4):
    N[0,i*3]=N0[i]
    N[1,i*3+1]=N0[i]
    N[0,i*3+2]=Nut[i]
    N[1,i*3+2]=Nvt[i]
    # N[0,i*3+2]=0
    # N[1,i*3+2]=0

# E0=E/(1-mu**2)
# mu0=mu/(1-mu)
E0,mu0=E,mu
D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu0)/2
D[0,1]=D[1,0]=mu0
D*=E0/(1-mu0**2)

X=np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],])
J=J2D(N0,X)

# def L2iso(xi,eta):
#     x=[x1,x2,x3,x4]
#     y=[y1,y2,y3,y4]
#     x=sum([N0[i]*x[i] for i in range(4)])
#     y=sum([N0[i]*y[i] for i in range(4)])
#     dds=lambda f: syp.diff(f,xi)
#     ddt=lambda f: syp.diff(f,eta)
#     ddx=lambda f: ddt(y)*dds(f)-dds(y)*ddt(f)
#     ddy=lambda f: dds(x)*ddt(f)-ddt(x)*dds(f)
#     return np.array([
#         [ddx,0],
#         [0,ddy],
#         [ddy,ddx]])/syp.det(J) 

def L2iso(xi,eta):
    x=[x1,x2,x3,x4]
    y=[y1,y2,y3,y4]
    x=sum([N0[i]*x[i] for i in range(4)])
    y=sum([N0[i]*y[i] for i in range(4)])
    diso= lambda f:syp.Matrix([[syp.diff(f,xi),syp.diff(f,eta)]]).T
    dnat= lambda f:syp.inv_quick(J)*diso(f)
    ddx=lambda f:dnat(f)[0]
    ddy=lambda f:dnat(f)[1]
    return np.array([
        [ddx,0],
        [0,ddy],
        [ddy,ddx]])

B=operator_dot(L2iso(xi,eta),N)
BDB=(B.T)*D*B
BDB_=t*BDB*syp.det(J) 

def get_binary_BDB():
    try:
        import metaGQ12
        bBDB=metaGQ12.autofunc_c
    except:
        raise Exception("Complile the cython code first!")
    return bBDB

def generate_code():
    tmp=os.path.dirname(os.path.realpath(__file__))
    logging.info("first time calling, compiling ")
    autowrap(BDB_,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython',tempdir=tmp,)

if __name__=='__main__':
    generate_code()