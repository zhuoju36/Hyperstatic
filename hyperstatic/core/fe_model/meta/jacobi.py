import sympy as syp
import numpy as np

l=syp.symbols("l")
xi,eta,zeta=syp.symbols("xi eta zeta")
x,y,z=syp.symbols("x y z")
ddx=lambda f : syp.diff(f,x)
ddy=lambda f : syp.diff(f,y)
ddz=lambda f : syp.diff(f,z)
ddxi=lambda f : syp.diff(f,xi)
ddeta=lambda f : syp.diff(f,eta)
ddzeta=lambda f : syp.diff(f,zeta)

def J2D(N:list,X:np.array):
    """Jacobi 2D matrix

    Args:
        N (list): n functions of xi and eta
        X (np.array): nx2 array

    Returns:
        syp.Matrix: Jacobi 2D matrix
    """
    n=len(N)
    J=syp.zeros(2,n)
    for i in range(n):
        J[0,i]=ddxi(N[i])
        J[1,i]=ddeta(N[i])
    return J*X

def J3D():
    pass