import os
import sympy as syp
from sympy.utilities.autowrap import autowrap
import numpy as np
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,E,mu,t,xi,eta

x12=x1-x2
x23=x2-x3
x31=x3-x1
y12=y1-y2
y23=y2-y3
y31=y3-y1

x=[x23,x31,x12] #xij
y=[y23,y31,y12] #yij

l=[syp.sqrt(x23**2+y23**2),syp.sqrt(x31**2+y31**2),syp.sqrt(x12**2+y12**2),]

P=syp.zeros(1,3)
tt=syp.zeros(1,3)
q=syp.zeros(1,3)
r=syp.zeros(1,3)

for ij,k in zip([0,1,2],[0,1,2]):
    P[k]=     -6*x[ij]/l[ij]**2
    tt[k]=    -6*y[ij]/l[ij]**2
    q[k]=3*x[ij]*y[ij]/l[ij]**2
    r[k]=   3*y[ij]**2/l[ij]**2

P4,P5,P6=tuple(P)
t4,t5,t6=tuple(tt)
q4,q5,q6=tuple(q)
r4,r5,r6=tuple(r)

Hxxi=syp.Matrix([
    P6*(1-2*xi)+(P5-P6)*eta,
    q6*(1-2*xi)-(q5+q6)*eta,
    -4+6*(xi+eta)+r6*(1-2*xi)-eta*(r5+r6),
    -P6*(1-2*xi)+eta*(P4+P6),
     q6*(1-2*xi)-eta*(q6-q4),
    -2+6*xi+r6*(1-2*xi)+eta*(r4-r6),
    -eta*(P5+P4),
     eta*(q4-q5),
    -eta*(r5-r4)])

Hyxi=syp.Matrix([
      t6*(1-2*xi)+eta*(t5-t6),
    1+r6*(1-2*xi)-eta*(r5+r6),
    -q6*(1-2*xi)+eta*(q5+q6),
    -t6*(1-2*xi)+eta*(t4+t6),
    -1+r6*(1-2*xi)+eta*(r4-r6),
    -q6*(1-2*xi)-eta*(q4-q6),
    -eta*(t4+t5),
     eta*(r4-r5),
    -eta*(q4-q5)
    ])

Hxeta=syp.Matrix([
    -P5*(1-2*eta)-xi*(P6-P5),
     q5*(1-2*eta)-xi*(q5+q6),
    -4+6*(xi+eta)+r5*(1-2*eta)-xi*(r5+r6),
    xi*(P4+P6),
    xi*(q4-q6),
    -xi*(r6-r4),
    P5*(1-2*eta)-xi*(P4+P5),
    q5*(1-2*eta)+xi*(q4-q5),
    -2+6*eta+r5*(1-2*eta)+xi*(r4-r5),
    ])

Hyeta=syp.Matrix([
    -t5*(1-2*eta)-xi*(t6-t5),
    1+r5*(1-2*eta)-xi*(r5+r6),
    -q5*(1-2*eta)+xi*(q5+q6),
    xi*(t4+t6),
    xi*(r4-r6),
    -xi*(q4-q6),
    t5*(1-2*eta)-xi*(t4+t5),
    -1+r5*(1-2*eta)+xi*(r4-r5),
    -q5*(1-2*eta)-xi*(q4-q5),
    ])

B=syp.Matrix([y31*Hxxi.T+y12*Hxeta.T,
-x31*Hyxi.T-x12*Hyeta.T,
-x31*Hxxi.T-x12*Hxeta.T+y31*Hyxi.T+y12*Hyeta.T])

B/=(x31*y12-x12*y31) #2A=x31*y12-x12*y31

D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

BDB=B.T*D*B

def get_binary_BDB():
    try:
        import metaDKT
        bBDB=metaDKT.autofunc_c
    except:
        raise Exception("Complile the cython code first!")
    return bBDB

def generate_code():
    tmp=os.path.dirname(os.path.realpath(__file__))
    bBDB=autowrap(BDB,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3],backend='cython',tempdir=tmp)

if __name__=='__main__':
    generate_code()