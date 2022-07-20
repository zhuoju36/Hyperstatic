import sympy as syp
import numpy as np
from inspect import isfunction

x,y,z=syp.symbols("x y z")
ddx=lambda f : syp.diff(f,x)
ddy=lambda f : syp.diff(f,y)
ddz=lambda f : syp.diff(f,z)

L3=np.array([
    [ddx,0,0],
    [0,ddy,0],
    [0,0,ddz],
    [ddy,ddx,0],
    [0,ddz,ddy],
    [ddz,0,ddx]])

def L2(x:syp.Symbol,y:syp.Symbol):
    ddx=lambda f : syp.diff(f,x)
    ddy=lambda f : syp.diff(f,y)
    return np.array([
        [ddx,0],
        [0,ddy],
        [ddy,ddx]])

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