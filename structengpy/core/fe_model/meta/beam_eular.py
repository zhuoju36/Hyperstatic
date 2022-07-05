import numpy as np
import sympy as syp
from sympy.utilities.autowrap import autowrap
import scipy.sparse as spr

#Axial
xi=syp.symbols("xi")
rho,E,A,l=syp.symbols("rho E A l")
N1=0.5*(1-xi)
N2=0.5*(1+xi)
N=np.array([N1,N2]).reshape((1,2))
d_dxi=np.vectorize(lambda N:syp.diff(N,xi))
K=syp.Matrix(np.dot(d_dxi(N).T,d_dxi(N)))
K=2*E*A/l*syp.integrate(K,xi)
K=K.replace(xi,1)-K.replace(xi,-1)
M=syp.Matrix(np.dot(N.T,N))
M=2*rho*A/l*syp.integrate(M,xi)
M=M.replace(xi,1)-M.replace(xi,-1)

bfuncK1=autowrap(K,args=[E,A,l],backend="cython")
bfuncM1=autowrap(M,args=[rho,A,l],backend="cython")

#Bending
#2-axis
xi=syp.symbols("xi")
E,l,I=syp.symbols("E l I")
N1=1-3*xi**2+2*xi**3
N2=(xi-2*xi**2+xi**3)*l
N3=3*xi**2-2*xi**3
N4=(xi**3-xi**2)*l
N=np.array([N1,N2,N3,N4]).reshape((1,4))
d2_dxi2=np.vectorize(lambda N:syp.diff(syp.diff(N,xi),xi))
K=np.dot(d2_dxi2(N).T,d2_dxi2(N))
K=syp.Matrix(K)
K=E*I/l**3*syp.integrate(K,xi)
K=K.replace(xi,1)-K.replace(xi,0)
M=np.dot(N.T,N)
M=syp.Matrix(M)
M=rho*I/l**3*syp.integrate(M,xi)
M=M.replace(xi,1)-M.replace(xi,0)
bfuncK22=autowrap(K,args=[E,I,l],backend="cython")
bfuncM22=autowrap(M,args=[rho,I,l],backend="cython")

#3-axis
N=np.array([-N1,N2,-N3,N4]).reshape((1,4)) #note the deflection w direction are different.
d2_dxi2=np.vectorize(lambda N:syp.diff(syp.diff(N,xi),xi))
K=np.dot(d2_dxi2(N).T,d2_dxi2(N))
K=syp.Matrix(K)
K=E*I/l**3*syp.integrate(K,xi)
K=K.replace(xi,1)-K.replace(xi,0)
M=np.dot(N.T,N)
M=syp.Matrix(M)
M=rho*I/l**3*syp.integrate(M,xi)
M=M.replace(xi,1)-M.replace(xi,0)
bfuncK23=autowrap(K,args=[E,I,l],backend="cython")
bfuncM23=autowrap(M,args=[rho,I,l],backend="cython")

#Torsion
xi=syp.symbols("xi")
G,J,l=syp.symbols("G J l")
N1=0.5*(1-xi)
N2=0.5*(1+xi)
N=np.array([N1,N2]).reshape((1,2))
d_dxi=np.vectorize(lambda N:syp.diff(N,xi))
K=syp.Matrix(np.dot(d_dxi(N).T,d_dxi(N)))
K=syp.integrate(2*G*J/l*K,xi)
K=K.replace(xi,1)-K.replace(xi,-1)
M=syp.Matrix(np.dot(N.T,N))
M=2*rho*J/l*syp.integrate(M,xi)
M=M.replace(xi,1)-M.replace(xi,-1)
bfuncK3=autowrap(K,args=[G,J,l],backend="cython")
bfuncM3=autowrap(M,args=[rho,J,l],backend="cython")

def K(E,G,A,I2,I3,J,l):
    Kdata=[]
    Krow=[]
    Kcol=[]
    K1=bfuncK1(E,A,l)
    K22=bfuncK22(E,I2,l)
    K23=bfuncK23(E,I3,l)
    K3=bfuncK3(G,J,l)
    for i in range(2):
        for j in range(2):
            Kdata.append(K1[i,j])
            Krow.append(i*6)
            Kcol.append(j*6)
    for i in range(4):
        for j in range(4):
            Kdata.append(K22[i,j])
            Krow.append(i//2*6+i%2*4+1)
            Kcol.append(j//2*6+j%2*4+1)
    for i in range(4):
        for j in range(4):
            Kdata.append(K23[i,j])
            Krow.append(i//2*6+i%2*2+2)
            Kcol.append(j//2*6+j%2*2+2)
    for i in range(2):
        for j in range(2):
            Kdata.append(K3[i,j])
            Krow.append(i*6+3)
            Kcol.append(j*6+3)
    return spr.coo_matrix((Kdata,(Krow,Kcol)),shape=(12,12))

def M(rho,A,I2,I3,J,l):
    Mdata=[]
    Mrow=[]
    Mcol=[]
    M1=bfuncM1(rho,A,l)
    M22=bfuncM22(rho,I2,l)
    M23=bfuncM23(rho,I3,l)
    M3=bfuncM3(rho,J,l)
    for i in range(2):
        for j in range(2):
            Mdata.append(M1[i,j])
            Mrow.append(i*6)
            Mcol.append(j*6)
    for i in range(4):
        for j in range(4):
            Mdata.append(M22[i,j])
            Mrow.append(i//2*6+i%2*4+1)
            Mcol.append(j//2*6+j%2*4+1)
    for i in range(4):
        for j in range(4):
            Mdata.append(M23[i,j])
            Mrow.append(i//2*6+i%2*2+2)
            Mcol.append(j//2*6+j%2*2+2)
    for i in range(2):
        for j in range(2):
            Mdata.append(M3[i,j])
            Mrow.append(i*6+3)
            Mcol.append(j*6+3)
    return spr.coo_matrix((Mdata,(Mrow,Mcol)),shape=(12,12))