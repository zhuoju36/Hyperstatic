import logging
import os
import sys

import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from hyperstatic.core.fe_model.meta.interpolate import Lagrange
from hyperstatic.core.fe_model.meta.operator import L2,operator_dot
from hyperstatic.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,E,mu,t,xi,eta

x=[x1,y2,y3]
y=[y1,y2,y3]
A=syp.det(syp.Matrix(
    [[1,x1,y1],
    [1,x2,y2],
    [1,x3,y3]]
))/2

a=syp.zeros(1,3)
b=syp.zeros(1,3)
c=syp.zeros(1,3)

for i,j,m in zip([0,1,2],[1,2,0],[2,0,1]):
    a[i]=x[j]*y[m]-x[m]*y[j]
    b[i]=y[j]-y[m]
    c[i]=-x[j]+x[m]

N=syp.zeros(2,6)
for i in range(3):
    N[:,i*2:i*2+2]=1/2/A*(a[i]+b[i]*xi+b[i]*eta)*syp.eye(2,2)

E0,mu0=E,mu
D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu0)/2
D[0,1]=D[1,0]=mu0
D*=E0/(1-mu0**2)

B=operator_dot(L2(xi,eta),N)
BDB=(B.T)*D*B

def get_binary_BDB():
    """
      will be compiled first time call, then use the binary file afterwards

    Returns:
        return : numerical BᵀDB function. 
    """
    import metaT9
    bBDB=metaT9.autofunc_c
    return bBDB

def generate_code():
    tmp=os.path.dirname(os.path.realpath(__file__))
    logging.info("Compiling cython code...")
    autowrap(BDB,args=[E,mu,t,x1,y1,x2,y2,x3,y3],backend='cython',tempdir=tmp,)

if __name__=='__main__':
    generate_code()