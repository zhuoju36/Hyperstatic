import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from structengpy.core.fe_model.meta.interpolate import Lagrange
from structengpy.core.fe_model.meta.jacobi import J2D
from structengpy.core.fe_model.meta.operator import operator_dot
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,x4,y4,E,mu,t,xi,eta

xi0=[-1,1,1,-1]
eta0=[-1,-1,1,1]
x0=[x1,x2,x3,x4]
y0=[y1,y2,y3,y4]
N0=[]
Nut=[]
Nvt=[]

for i in range(4):
    a1=xi0[i]*x0[i]/4
    a2=eta0[i]*x0[i]/4
    a3=xi0[i]*eta0[i]*x0[i]/4
    b1=xi0[i]*y0[i]/4
    b2=eta0[i]*y0[i]/4
    b3=xi0[i]*eta0[i]*y0[i]/4    
    N0.append(0.25*(1+xi0[i]*xi)*(1+eta0[i]*eta))
    Nut.append((xi*(1-xi**2)*(b1+b3*eta0[i])*(1+eta0[i]*eta)+eta0[i]*(1-eta**2)*(b2+b3*eta0[i])*(1+eta0[i]*eta))/8)
    Nvt.append(-(xi*(1-xi**2)*(a1+a3*eta0[i])*(1+eta0[i]*eta)+eta0[i]*(1-eta**2)*(a2+a3*eta0[i])*(1+eta0[i]*eta))/8)
    
N=syp.zeros(2,3*4)
for i in range(4):
    N[0,i*3]=N0[i]
    N[1,i*3+1]=N0[i]
    N[0,i*3+2]=Nut[i]
    N[1,i*3+2]=Nvt[i]

from structengpy.core.fe_model.meta.operator import L2,operator_dot

D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
# D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

B=operator_dot(L2(xi,eta),N)
BDB=B.T*D*B

X=np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],])
detJ=syp.det(J2D(N0,X)) 

def get_binary_BDB():
    bBDB=autowrap(BDB*detJ,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython')
    return bBDB