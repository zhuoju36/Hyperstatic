import sympy as syp
import numpy as np

# L=[L1,L2,L3]
# N=syp.zeros(1,6)
# for i in range(3):
#     N[i]=L[i](2*L[i]-1)
# for i in range(3):
#     N[i+3]=4*L[i]*L[i%2]

# for i,j,k in zip([1,2,3],[2,3,1],[3,1,2]):
#     b[i]=y[j]-y[k],c[i]=x[k]-x[j]
#     p[i]=6*c[i]/l[jk]**2
#     p[i]=6*b[i]/l[jk]**2
#     r[i]=3*c[i]**2/l[jk]**2
#     s[i]=3*b[i]**2/l[jk]**2
#     v[i]=3*b[i]*c[i]/l[jk]**2

# for i,j,k in zip([1,2,3],[2,3,1],[3,1,2]):
#     Hwx=-p[k]*L[i]*L[j]+p[j]*L[i]*L[k]
#     Hpxx=L[i]-r[k]*L[i]*L[j]-r[j]*L[i]*L[k]
#     Hpyx=v[k]*L[i]*L[j]+v[j]*L[i]*L[k]

#     Hwy=q[k]*L[i]*L[j]-q[j]*L[i]*L[k]
#     Hpxy=v[k]*L[i]*L[j]+v[j]*L[i]*L[k]
#     Hpyy=L[i]-s[k]*L[i]*L[j]-s[j]*L[i]*L[k]

# coef[0,0]=1

# coef=syp.zeros(6,9)
# coef[0,0]=-3*x12/2*l12**2
# coef[0,1]=-3*y12/2*l12**2
# coef[0,4]=3*x31/2*l31**2
# coef[0,5]=3*y31/2*l31**2

# coef[1,0]=(2*y12**2-x12**2)/4/l12**2
# coef[1,1]=-3*x12*y12**2/4/l12**2
# coef[1,4]=(2*y31**2-x31**2)/4/l31**2
# coef[1,5]=-3*x31*y31/4*l31**2

# coef[2,0]=-3*x12*y12/4*l12**2
# coef[2,1]=(2*x12**2-y12**2)/4/l12**2
# coef[2,4]=-3*x31*y31/4*l31**2
# coef[2,5]=(2*x31**2-y31**2)/4/l31**2

# coef[3,0]=3*x12/2*l12**2
# coef[3,1]=3*y12/2*l12**2
# coef[3,2]=-3*x23/2*l23**2
# coef[3,3]=-3*y23/2*l23**2

# coef[4,0]=(2*y12**2-x12**2)/4/l12**2
# coef[4,1]=-3*x12*y12**2/4/l12**2
# coef[4,2]=(2*y23**2-x23**2)/4/l23**2
# coef[4,3]=-3*x23*y23/4*l23**2

# coef[5,0]=-3*x12*y12/4*l12**2
# coef[5,1]=(2*x12**2-y12**2)/4/l12**2
# coef[5,2]=-3*x23*y23/4*l23**2
# coef[5,3]=(2*x23**2-y23**2)/4/l23**2

# coef[6,0]=3*x23/2*l23**2
# coef[6,1]=3*y23/2*l23**2
# coef[6,4]=-3*x31/2*l31**2
# coef[6,5]=-3*y31/2*l31**2

# coef[7,0]=(2*y23**2-x23**2)/4/l23**2
# coef[7,1]=-3*x23*y23**2/4/l23**2
# coef[7,4]=(2*y31**2-x31**2)/4/l31**2
# coef[7,5]=-3*x31*y31/4*l31**2

# coef[8,0]=-3*x23*y23/4*l23**2
# coef[8,1]=(2*x23**2-y23**2)/4/l23**2
# coef[8,4]=-3*x31*y31/4*l31**2
# coef[8,5]=(2*x31**2-y31**2)/4/l31**2

import sympy as syp
import numpy as np
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,E,mu,t,xi,eta

x12=x1-x2
x23=x2-x3
x31=x3-x1
y12=y1-y2
y23=y2-y3
y31=y3-y1

x=[x23,x31,x12] #xij
y=[y23,y31,y12] #xij

l=[syp.sqrt((x2-x3)**2+(y2-y3)**2),syp.sqrt((x3-x1)**2+(y3-y1)**2),syp.sqrt((x1-x2)**2+(y1-y2)**2),]

P=syp.zeros(1,3)
t=syp.zeros(1,3)
q=syp.zeros(1,3)
r=syp.zeros(1,3)

for ij,k in zip([0,1,2],[0,1,2]):
    P[k]=-6*x[ij]/l[ij]**2
    t[k]=-6*y[ij]/l[ij]**2
    q[k]=3*x[ij]*y[ij]/l[ij]**2
    r[k]=3*y[ij]**2/l[ij]**2

P4,P5,P6=tuple(P)
t4,t5,t6=tuple(t)
q4,q5,q6=tuple(q)
r4,r5,r6=tuple(r)

Hxxi=syp.Matrix([
    P6*(1-2*xi)+(P5-P6)*eta,
    q6*(1-2*xi)-(q5+q6)*eta,
    -4+6*(eta+xi)+r6*(1-2*xi)-eta*(r5+r6),
    -P6*(1-2*xi)+eta*(P4+P6),
    q6*(1-2*xi)-eta*(q6-q4),
    -2+6*xi+r6*(1-2*xi)+eta*(r4-r6),
    -eta*(P5+P4),
    eta*(q4-q5),
    -eta*(r5-r4)])

Hyxi=syp.Matrix([
    t6*(1-2*xi)+(t5-t6)*eta,
    1+r6*(1-2*xi)-(r5+r6)*eta,
    -q6*(1-2*xi)-eta*(r5+r6),
    -t6*(1-2*xi)+eta*(t4+t6),
    -1+r6*(1-2*xi)+(r4-r6)*eta,
    -q6*(1-2*xi)-eta*(q4-q6),
    -eta*(t4+t5),
    eta*(r4-r5),
    -eta*(q4-q5)
    ])

Hxeta=syp.Matrix([
    P5*(1-2*eta)+(P6-P5)*xi,
    q5*(1-2*eta)-(q5+q6)*xi,
    -4+6*(eta+xi)+r5*(1-2*eta)-xi*(r5+r6),
    xi*(P4+P6),
    xi*(q4-q6),
    -xi*(r6-r4),
    P5*(1-2*eta)-xi*(P4+P5),
    q5*(1-2*eta)+xi*(q4-q5),
    -2+6*eta+r5*(1-2*xi)+xi*(r4-r5),
    ])

Hyeta=syp.Matrix([
    -t5*(1-2*eta)-(t6-t5)*xi,
    1+r5*(1-2*eta)-(r5+r6)*xi,
    -q5*(1-2*xi)-xi*(q5+q6),
    xi*(t4+t6),
    xi*(r4-r6),
    -xi*(q4-q6),
    t5*(1-2*eta)-eta*(t4+t5),
    -1+r5*(1-2*eta)+(r4-r5)*xi,
    -q5*(1-2*eta)-xi*(q4-q5),
    ])

B=syp.Matrix([y31*Hxxi.T+y12*Hxeta.T,
-x31*Hyxi.T-x12*Hyeta.T,
-x31*Hxxi.T-x12*Hyeta.T+y31*Hyxi.T+y12*Hyeta.T])

B/=(x31*y12-x12*y31) #2A=x31*y12-x12*y31

D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

BDB=B.T*D*B