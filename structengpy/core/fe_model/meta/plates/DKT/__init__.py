import sympy as syp
import numpy as np

L=[L1,L2,L3]
N=syp.zeros(1,6)
for i in range(3):
    N[i]=L[i](2*L[i]-1)
for i in range(3):
    N[i+3]=4*L[i]*L[i%2]

for i,j,k in zip([1,2,3],[2,3,1],[3,1,2]):
    b[i]=y[j]-y[k],c[i]=x[k]-x[j]
    p[i]=6*c[i]/l[jk]**2
    p[i]=6*b[i]/l[jk]**2
    r[i]=3*c[i]**2/l[jk]**2
    s[i]=3*b[i]**2/l[jk]**2
    v[i]=3*b[i]*c[i]/l[jk]**2

for i,j,k in zip([1,2,3],[2,3,1],[3,1,2]):
    Hwx=-p[k]*L[i]*L[j]+p[j]*L[i]*L[k]
    Hpxx=L[i]-r[k]*L[i]*L[j]-r[j]*L[i]*L[k]
    Hpyx=v[k]*L[i]*L[j]+v[j]*L[i]*L[k]

    Hwy=q[k]*L[i]*L[j]-q[j]*L[i]*L[k]
    Hpxy=v[k]*L[i]*L[j]+v[j]*L[i]*L[k]
    Hpyy=L[i]-s[k]*L[i]*L[j]-s[j]*L[i]*L[k]
