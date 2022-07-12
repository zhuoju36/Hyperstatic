import numpy as np
import sympy as syp
from sympy import tensor as syt
from sympy.utilities.autowrap import autowrap


kdelta=syp.KroneckerDelta
E,nu=syp.symbols("E nu")
G=E/2/(1+nu)
lamda=E*nu/(1+nu)/(1-2*nu)

D_ijkl=lambda i,j,k,l:2*G*kdelta(i,k)*kdelta(j,l)+lamda*kdelta(i,j)*kdelta(k,l)

D=syt.Array.zeros(3,3,3,3)
D=D.as_mutable()
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                D[i,j,k,l] = 2*G*kdelta(i,k)*kdelta(j,l)+lamda*kdelta(i,j)*kdelta(k,l)

# eps=syp.zeros(3,3)
eps=syt.Array.zeros(3,3).as_mutable()
exx,eyy,ezz,gxy,gyz,gzx=syp.symbols("\epsilon_{xx},\epsilon_{yy},\epsilon_{zz},\gamma_{xy},\gamma_{yz},\gamma_{zx}")
eps[0,0],eps[1,1],eps[2,2],eps[0,1],eps[1,2],eps[2,0]=exx,eyy,ezz,gxy/2,gyz/2,gzx/2
eps[1,0],eps[2,1],eps[0,2]=eps[0,1],eps[1,2],eps[2,0]
eps

sig=np.tensordot(D,eps)
sig=syt.Array(sig)
sig