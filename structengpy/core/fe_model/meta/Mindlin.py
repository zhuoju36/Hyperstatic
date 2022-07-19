import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
from structengpy.core.fe_model.meta.interpolate import Lagrange
from structengpy.core.fe_model.meta.jacobi import J2D

from inspect import isfunction

E,mu,t=syp.symbols("E mu t")
xi,eta=syp.symbols("xi eta")
G=E/2/(1+mu)
k=6/5
alpha=G*t/k

x,y=syp.symbols("xi eta")
ddx=lambda f : syp.diff(f,x)
ddy=lambda f : syp.diff(f,y)
Lb=np.array([
    [ddx,0,0],
    [0,ddy,0],
    [ddy,ddx,0]])

Ls=np.array([
    [-1,0,ddx],
    [0,-1,ddy],
    ])

def operator_dot(A,f):
    assert A.shape[1]==f.shape[0]
    res=syp.zeros(A.shape[0],f.shape[1])
    for i in range(A.shape[0]):
        for j in range(f.shape[1]):
            for k in range(A.shape[1]):
                if A[i,k]!=0:
                    if isfunction(A[i,k]):
                        res[i,j]+=A[i,k](f[k,j])
                    else:
                        res[i,j]+=A[i,k]*f[k,j]
    return res

N1,N2,N3,N4=tuple(Lagrange.N2D())

N=syp.zeros(3,12)
N[:,:3]=syp.eye(3,3)*N1#,syp.eye()*N2,syp.eye()*N3,syp.eye()*N4]
N[:,3:6]=syp.eye(3,3)*N2#,syp.eye()*N2,syp.eye()*N3,syp.eye()*N4]
N[:,6:9]=syp.eye(3,3)*N3#,syp.eye()*N2,syp.eye()*N3,syp.eye()*N4]
N[:,9:12]=syp.eye(3,3)*N4#,syp.eye()*N2,syp.eye()*N3,syp.eye()*N4]
Bb=-operator_dot(Lb,N)
Bs=operator_dot(Ls,N)


D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

BDBb=(Bb.T)*(D)*Bb
BBs=Bs.T*Bs

x1,y1=syp.symbols("x1 y1")
x2,y2=syp.symbols("x2 y2")
x3,y3=syp.symbols("x3 y3")
x4,y4=syp.symbols("x4 y4")
X=np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],])
BDB=(BDBb+alpha*BBs)*syp.det(J2D([N1,N2,N3,N4],X))
bBDB=autowrap(BDB,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython')
