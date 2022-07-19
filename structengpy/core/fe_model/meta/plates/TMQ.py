import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from structengpy.core.fe_model.meta.interpolate import Lagrange
from structengpy.core.fe_model.meta.jacobi import J2D
from structengpy.core.fe_model.meta.operator import operator_dot
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,x4,y4

alpha=syp.zeros(4,12)
beta=syp.zeros(4,12)

E,mu,t=syp.symbols("E mu t")
xi,eta=syp.symbols("xi eta")

b1=y2-y3
b2=y3-y4
b3=y4-y1
b4=y1-y2
c1=x3-x2
c2=x4-x3
c3=x1-x4
c4=x2-x1

d1=syp.sqrt((x2-x3)**2+(y2-y3)**2)
d2=syp.sqrt((x3-x4)**2+(y3-y4)**2)
d3=syp.sqrt((x4-x1)**2+(y4-y1)**2)
d4=syp.sqrt((x1-x2)**2+(y1-y2)**2)

delta1=(t/d1)**2/(5/6*(1-mu)+2*(t/d1)**2)
delta2=(t/d2)**2/(5/6*(1-mu)+2*(t/d2)**2)
delta3=(t/d3)**2/(5/6*(1-mu)+2*(t/d3)**2)
delta4=(t/d4)**2/(5/6*(1-mu)+2*(t/d4)**2)

G=E/2/(1+mu)
k=6/5
C=G*t/k

x,y=syp.symbols("xi eta")
ddx=lambda f : syp.diff(f,x)
ddy=lambda f : syp.diff(f,y)
L0=np.array([
    [0,ddx,0],
    [0,0,ddy],
    [0,ddy,ddx]])

L1=np.array([
    [ddx,0,ddy],
    ]).T

L2=np.array([
    [0,ddx,ddy],
    ]).T

alpha[2,0]=3*c3/2/d3**2*(1-2*delta3)
alpha[3,0]=-3*c4/2/d4**2*(1-2*delta4)
alpha[2,1]=(b3**2-c3**2/2*(1-6*delta3))/2/d3**2
alpha[3,1]=(b4**2-c4**2/2*(1-6*delta4))/2/d4**2
alpha[2,2]=3*b3*c3/4/d3**2*(1-2*delta3)
alpha[3,2]=3*b4*c4/4/d4**2*(1-2*delta4)
alpha[0,3]=-3*c1/2/d1**2*(1-2*delta1)
alpha[3,3]=3*c4/2/d4**2*(1-2*delta4)
alpha[0,4]=(b1**2-c1**2/2*(1-6*delta1))/2/d1**2
alpha[3,4]=(b4**2-c4**2/2*(1-6*delta4))/2/d4**2
alpha[0,5]=3*b1*c1/4/d1**2*(1-2*delta1)
alpha[3,5]=3*b4*c4/4/d4**2*(1-2*delta4)
alpha[0,6]=3*c1/2/d1**2*(1-2*delta1)
alpha[1,6]=-3*c2/2/d2**2*(1-2*delta2)
alpha[0,7]=(b1**2-c1**2/2*(1-6*delta1))/2/d1**2
alpha[1,7]=(b2**2-c2**2/2*(1-6*delta2))/2/d2**2
alpha[0,8]=3*b1*c1/4/d1**2*(1-2*delta1)
alpha[1,8]=-3*b2*c2/4/d2**2*(1-2*delta2)
alpha[1,9]=3*c2/2/d2**2*(1-2*delta2)
alpha[2,9]=-3*c3/2/d3**2*(1-2*delta3)
alpha[1,10]=(b2**2-c2**2/2*(1-6*delta2))/2/d2**2
alpha[2,10]=(b3**2-c3**2/2*(1-6*delta3))/2/d3**2
alpha[1,11]=3*b2*c2/4/d2**2*(1-2*delta2)
alpha[2,11]=3*b3*c3/4/d3**2*(1-2*delta3)

beta[2,0]=-3*c3/2/d3**2*(1-2*delta3)
beta[3,0]=3*c4/2/d4**2*(1-2*delta4)
beta[2,1]=3*b3*c3/4/d3**2*(1-2*delta3)
beta[3,1]=3*b4*c4/4/d4**2*(1-2*delta4)
beta[2,2]=(c3**2-b3**2/2*(1-6*delta3))/2/d3**2
beta[3,2]=(c4**2-b4**2/2*(1-6*delta4))/2/d4**2
beta[0,3]=3*b1/2/d1**2*(1-2*delta1)
beta[3,3]=-3*b4/2/d4**2*(1-2*delta4)
beta[0,4]=3*b1*c1/4/d1**2*(1-2*delta1)
beta[3,4]=3*b4*c4/4/d4**2*(1-2*delta4)
beta[0,5]=(c1**2-b1**2/2*(1-6*delta1))/2/d1**2
beta[3,5]=(c4**2-b4**2/2*(1-6*delta4))/2/d4**2
beta[0,6]=-3*b1/2/d1**2*(1-2*delta1)
beta[1,6]=3*b2/2/d2**2*(1-2*delta2)
beta[0,7]=3*b1*c1/4/d1**2*(1-2*delta1)
beta[1,7]=3*b2*c2/4/d2**2*(1-2*delta2)
beta[0,8]=(c1**2-b1**2/2*(1-6*delta1))/2/d1**2
beta[1,8]=(c2**2-b2**2/2*(1-6*delta2))/2/d2**2
beta[1,9]=-3*c2/2/d2**2*(1-2*delta2)
beta[2,9]=3*c3/2/d3**2*(1-2*delta3)
beta[1,10]=3*b2*c2/4/d2**2*(1-2*delta2)
beta[2,10]=3*b3*c3/4/d3**2*(1-2*delta3)
beta[1,11]=(c2**2-b2**2/2*(1-6*delta2))/2/d2**2
beta[2,11]=(c3**2-b3**2/2*(1-6*delta3))/2/d3**2

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
H0=operator_dot(L0,N)

N=syp.zeros(1,4)
N[0]=N1
N[1]=N2
N[2]=N3
N[3]=N4
H1=operator_dot(L1,N)

N=syp.zeros(1,4)
N[0]=N1
N[1]=N2
N[2]=N3
N[3]=N4
H2=operator_dot(L2,N)

D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

Bb=-H0+H1*alpha+H2*beta

BDBb=Bb.T*D*Bb

#shear
N1=0.25*(1-xi)*(1-eta)
N2=0.25*(1+xi)*(1-eta)
N3=0.25*(1+xi)*(1+eta)
N4=0.25*(1-xi)*(1+eta)

Ns=syp.zeros(1,4)
Ns[0]=N1
Ns[1]=N2
Ns[2]=N3
Ns[3]=N4

Xs=syp.zeros(4,4)
Ys=syp.zeros(4,4)

Xs[1,0]=b4/(b4*c1-b1*c4)
Xs[2,0]=-b2/(b1*c2-b2*c1)
Xs[2,1]=b1/(b1*c2-b2*c1)
Xs[3,1]=-b3/(b2*c3-b3*c2)
Xs[0,2]=-b4/(b4*c3-b3*c4)
Xs[3,2]=b2/(b3*c2-b2*c3)
Xs[0,3]=b3/(b4*c3-b3*c4)
Xs[1,3]=-b1/(b4*c1-b1*c4)

Ys[1,0]=c4/(b4*c1-b1*c4)
Ys[2,0]=-c2/(b1*c2-b2*c1)
Ys[2,1]=c1/(b1*c2-b2*c1)
Ys[3,1]=-c3/(b2*c3-b3*c2)
Ys[0,2]=-c4/(c4*b3-c3*b4)
Ys[3,2]=c2/(c3*b2-c2*b3)
Ys[0,3]=c3/(c4*b3-c3*b4)
Ys[1,3]=-b1/(b4*c1-b1*c4)

Gamma=syp.zeros(4,12)
Gamma[2,0]=2*delta3
Gamma[3,0]=-2*delta4
Gamma[2,1]=-c3*delta3
Gamma[3,1]=-c4*delta4
Gamma[2,2]=b3*delta3
Gamma[3,2]=b4*delta4
Gamma[0,3]=-2*delta1
Gamma[3,3]=2*delta4
Gamma[0,4]=-c1*delta1
Gamma[3,4]=-c4*delta4
Gamma[0,5]=b1*delta1
Gamma[3,5]=b4*delta4
Gamma[0,6]=2*delta1
Gamma[1,6]=-2*delta1
Gamma[0,7]=-c1*delta2
Gamma[1,7]=-c2*delta2
Gamma[0,8]=b1*delta1
Gamma[1,8]=b2*delta2
Gamma[1,9]=2*delta1
Gamma[2,9]=-2*delta2
Gamma[1,10]=-c2*delta2
Gamma[2,10]=-c3*delta3
Gamma[1,11]=b2*delta2
Gamma[2,11]=b3*delta3

Bs=syp.zeros(2,12)
Bs[0,:]=Ns*Xs*Gamma
Bs[1,:]=Ns*Ys*Gamma
BCBs=Bs.T*C*syp.eye(2)*Bs

bBDBb=autowrap(BDBb,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython')

bBDBs=autowrap(BCBs,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython')
