import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from structengpy.core.fe_model.meta.interpolate import Lagrange
from structengpy.core.fe_model.meta.jacobi import J2D
from structengpy.core.fe_model.meta.operator import operator_dot

alpha=syp.zeros(4,12)
beta=syp.zeros(4,12)

E,mu,t=syp.symbols("E mu t")
xi,eta=syp.symbols("xi eta")
G=E/2/(1+mu)
k=6/5
alpha=G*t/k

x,y=syp.symbols("xi eta")
ddx=lambda f : syp.diff(f,x)
ddy=lambda f : syp.diff(f,y)
L0=np.array([
    [0,ddx,0],
    [0,0,ddy],
    [0,ddy,ddx]])

L1=np.array([
    [ddx,0,ddy],
    ])

L1=np.array([
    [0,ddx,ddy],
    ])

# alpha[2,0]=3*c3/2/d3**2*(1-2*delta3)
# alpha[3,0]=-3*c4/2/d4**2*(1-2*delta4)
# alpha[2,1]=(b3**2-c3**2/2*(1-6*delta3))/2/d3**2
# alpha[3,1]=(b4**2-c4**2/2*(1-6*delta4))/2/d4**2
# alpha[2,2]=3*b3*c3/4/d3**2*(1-2*delta3)
# alpha[3,2]=3*b4*c4/4/d4**2*(1-2*delta4)
# alpha[0,3]=-3*c1/2/d1**2*(1-2*delta1)
# alpha[3,3]=3*c4/2/d4**2*(1-2*delta4)
# alpha[0,4]=(b1**2-c1**2/2*(1-6*delta1))/2/d1**2
# alpha[3,4]=(b4**2-c4**2/2*(1-6*delta4))/2/d4**2
# alpha[0,5]=3*b1*c1/4/d1**2*(1-2*delta1)
# alpha[3,5]=3*b4*c4/4/d4**2*(1-2*delta4)
# alpha[0,6]=3*c1/2/d1**2*(1-2*delta1)
# alpha[1,6]=-3*c2/2/d2**2*(1-2*delta2)
# alpha[0,7]=(b1**2-c1**2/2*(1-6*delta1))/2/d1**2
# alpha[1,7]=(b2**2-c2**2/2*(1-6*delta2))/2/d2**2
# alpha[0,8]=3*b1*c1/4/d1**2*(1-2*delta1)
# alpha[1,8]=-3*b2*c2/4/d2**2*(1-2*delta2)
# alpha[1,9]=3*c2/2/d2**2*(1-2*delta2)
# alpha[2,9]=-3*c3/2/d3**2*(1-2*delta3)
# alpha[1,10]=(b2**2-c2**2/2*(1-6*delta2))/2/d2**2
# alpha[2,10]=(b3**2-c3**2/2*(1-6*delta3))/2/d3**2
# alpha[1,11]=3*b2*c2/4/d2**2*(1-2*delta2)
# alpha[2,11]=3*b3*c3/4/d3**2*(1-2*delta3)

# beta[2,0]=-3*c3/2/d3**2*(1-2*delta3)
# beta[3,0]=3*c4/2/d4**2*(1-2*delta4)
# beta[2,1]=3*b3*c3/4/d3**2*(1-2*delta3)
# beta[3,1]=3*b4*c4/4/d4**2*(1-2*delta4)
# beta[2,2]=(c3**2-b3**2/2*(1-6*delta3))/2/d3**2
# beta[3,2]=(c4**2-b4**2/2*(1-6*delta4))/2/d4**2
# beta[0,3]=3*b1/2/d1**2*(1-2*delta1)
# beta[3,3]=-3*b4/2/d4**2*(1-2*delta4)
# beta[0,4]=3*b1*c1/4/d1**2*(1-2*delta1)
# beta[3,4]=3*b4*c4/4/d4**2*(1-2*delta4)
# beta[0,5]=(c1**2-b1**2/2*(1-6*delta1))/2/d1**2
# beta[3,5]=(c4**2-b4**2/2*(1-6*delta4))/2/d4**2
# beta[0,6]=-3*b1/2/d1**2*(1-2*delta1)
# beta[1,6]=3*b2/2/d2**2*(1-2*delta2)
# beta[0,7]=3*b1*c1/4/d1**2*(1-2*delta1)
# beta[1,7]=3*b2*c2/4/d2**2*(1-2*delta2)
# beta[0,8]=(c1**2-b1**2/2*(1-6*delta1))/2/d1**2
# beta[1,8]=(c2**2-b2**2/2*(1-6*delta2))/2/d2**2
# beta[1,9]=-3*c2/2/d2**2*(1-2*delta2)
# beta[2,9]=3*c3/2/d3**2*(1-2*delta3)
# beta[1,10]=3*b2*c2/4/d2**2*(1-2*delta2)
# beta[2,10]=3*b3*c3/4/d3**2*(1-2*delta3)
# beta[1,11]=(c2**2-b2**2/2*(1-6*delta2))/2/d2**2
# beta[2,11]=(c3**2-b3**2/2*(1-6*delta3))/2/d3**2

N1=-0.25*(1-xi)*(1-eta)*(1+xi+eta)
N2=-0.25*(1+xi)*(1-eta)*(1-xi+eta)
N3=-0.25*(1+xi)*(1+eta)*(1-xi-eta)
N4=-0.25*(1-xi)*(1+eta)*(1+xi-eta)
N5=0.25*(1-xi**2)*(1+eta)
N6=0.25*(1-xi**2)*(1+eta)
N7=0.25*(1-xi**2)*(1-eta)
N8=0.25*(1-xi**2)*(1-eta)

N=syp.zeros(3,12)
N[:,:3]=syp.eye(3,3)*N1
N[:,3:6]=syp.eye(3,3)*N2
N[:,6:9]=syp.eye(3,3)*N3
N[:,9:12]=syp.eye(3,3)*N4

operator_dot(L0,N1)