import os
import sympy as syp
from sympy.utilities.autowrap import autowrap
import numpy as np
from structengpy.core.fe_model.meta.plates import x1,y1,x2,y2,x3,y3,x4,y4,E,mu,t,xi,eta
from structengpy.core.fe_model.meta.operator import operator_dot
from structengpy.core.fe_model.meta.jacobi import J2D

x12=x1-x2
x23=x2-x3
x34=x3-x4
x41=x4-x1
y12=y1-y2
y23=y2-y3
y34=y3-y4
y41=y4-y1

x=[x12,x23,x34,x41] #xij
y=[y12,y23,y34,y41] #yij
l2=[x12**2+y12**2,x23**2+y23**2,x34**2+y34**2,x41**2+y41**2]

a=syp.zeros(1,4)
b=syp.zeros(1,4)
c=syp.zeros(1,4)
d=syp.zeros(1,4)
e=syp.zeros(1,4)

for ij,k in zip([0,1,2,3],[0,1,2,3]):
    a[k]=     -x[ij]/l2[ij]
    b[k]=     0.75*x[ij]*y[ij]/l2[ij]
    c[k]=     (0.25*x[ij]**2-0.5*y[ij]**2)/l2[ij]
    d[k]=     -y[ij]/l2[ij]
    e[k]=     (-0.5*x[ij]**2+0.25*y[ij]**2)/l2[ij]

a5,a6,a7,a8=tuple(a)
b5,b6,b7,b8=tuple(b)
c5,c6,c7,c8=tuple(c)
d5,d6,d7,d8=tuple(d)
e5,e6,e7,e8=tuple(e)

# xi0 =[-1,1,1,-1]
# eta0=[-1,-1,1,1]
N1=-0.25*(1-xi)*(1-eta)*(1+xi+eta)
N2=-0.25*(1+xi)*(1-eta)*(1-xi+eta)
N3=-0.25*(1+xi)*(1+eta)*(1-xi-eta)
N4=-0.25*(1-xi)*(1+eta)*(1+xi-eta)
# N5=0.5*(1-eta**2)*(1+xi)
# N6=0.5*(1-xi**2)*(1+eta)
# N7=0.5*(1-eta**2)*(1-xi)
# N8=0.5*(1-xi**2)*(1-eta)
N5=0.5*(1-xi**2)*(1-eta)
N6=0.5*(1-eta**2)*(1+xi)
N7=0.5*(1-xi**2)*(1+eta)
N8=0.5*(1-eta**2)*(1-xi)

Hx1=1.5*(a5*N5-a8*N8)
Hx2=b5*N5+b8*N8
Hx3=N1-c5*N5-c8*N8
Hy1=1.5*(d5*N5-d8*N8)
Hy2=-N1+e5*N5+e8*N8
Hy3=-b5*N5-b8*N8

Hx4=1.5*(a6*N6-a5*N5)
Hx5=b6*N6+b5*N5
Hx6=N2-c6*N6-c5*N5
Hy4=1.5*(d6*N6-d5*N5)
Hy5=-N2+e6*N6+e5*N5
Hy6=-b6*N6-b5*N5

Hx7=1.5*(a7*N7-a6*N6)
Hx8=b7*N7+b6*N6
Hx9=N3-c7*N7-c6*N6
Hy7=1.5*(d7*N7-d6*N6)
Hy8=-N3+e7*N7+e6*N6
Hy9=-b7*N7-b6*N6

Hx10=1.5*(a8*N8-a7*N7)
Hx11=b8*N8+b7*N7
Hx12=N4-c8*N8-c7*N7
Hy10=1.5*(d8*N8-d7*N7)
Hy11=-N4+e8*N8+e7*N7
Hy12=-b8*N8-b7*N7

Hx=syp.Array([Hx1,Hx2,Hx3,Hx4,Hx5,Hx6,Hx7,Hx8,Hx9,Hx10,Hx11,Hx12])
Hy=syp.Array([Hy1,Hy2,Hy3,Hy4,Hy5,Hy6,Hy7,Hy8,Hy9,Hy10,Hy11,Hy12])
H=syp.Array([Hx,Hy])

x21=x2-x1
y21=y2-y1
x32=x3-x2
y32=y3-y2
x42=x4-x2
x31=x3-x1
y42=y4-y2
y31=y3-y1

J11=0.25*(x21+x34+eta*(x12+x34))
J12=0.25*(y21+y34+eta*(y12+y34))
J21=0.25*(x32+x41+xi*(x12+x34))
J22=0.25*(y32+y41+xi*(y12+y34))

J=syp.Matrix([[J11,J12],[J21,J22]])

detJ=1/8*(y42*x31-y31*x42)+xi/8*(y34*x21-y21*x34)+eta/8*(y41*x32-y32*x41)
j11=J11/detJ
j12=-J12/detJ
j21=-J21/detJ
j22=J22/detJ

ddx=lambda f : syp.diff(f,xi)
ddy=lambda f : syp.diff(f,eta)
B=syp.Matrix(
    [j11*ddx(Hx)+j12*ddy(Hx),
    j21*ddx(Hy)+j22*ddy(Hy),
j11*ddx(Hy)+j12*ddy(Hy)+j21*ddx(Hx)+j22*ddy(Hx)])

D=syp.eye(3,3)
D[0,0]=D[1,1]=1
D[2,2]=(1-mu)/2
D[0,1]=D[1,0]=mu
D*=E*t**3/12/(1-mu**2)

# X=np.array([[x1,y1],[x2,y2],[x3,y3],[x4,y4],])
# J=J2D([N1,N2,N3,N4],X)

# def L0iso(xi,eta):
#     # _x=[x1,x2,x3,x4,(x1+x2)/2,(x2+x3)/2,(x3+x4)/2,(x4+x1)/2]
#     # _y=[y1,y2,y3,y4,(y1+y2)/2,(y2+y3)/2,(y3+y4)/2,(y4+y1)/2]
#     # _x=sum([H[i]*x[i] for i in range(8)])
#     # _y=sum([H[i]*y[i] for i in range(8)])
#     diso= lambda f:syp.Matrix([[syp.diff(f,xi),syp.diff(f,eta)]]).T
#     dnat= lambda f:syp.inv_quick(J)*diso(f)
#     ddx=lambda f:dnat(f)[0]
#     ddy=lambda f:dnat(f)[1]
#     return np.array([
#         [ddx,0],
#         [0,ddy],
#         [ddy,ddx]])

# N=syp.zeros(3,12)
# N[:,:3]=syp.eye(3,3)*N1
# N[:,3:6]=syp.eye(3,3)*N2
# N[:,6:9]=syp.eye(3,3)*N3
# N[:,9:12]=syp.eye(3,3)*N4
# B=operator_dot(L0iso(xi,eta),H)

BDB=B.T*D*B*syp.det(J)

def get_binary_BDB():
    try:
        import metaDKQ
        bBDB=metaDKQ.autofunc_c
    except:
        raise Exception("Complile the cython code first!")
    return bBDB

def generate_code():
    tmp=os.path.dirname(os.path.realpath(__file__))
    autowrap(BDB,args=[E,mu,t,xi,eta,x1,y1,x2,y2,x3,y3,x4,y4],backend='cython',tempdir=tmp)
    name='metaDKQ'
    os.rename(os.path.join(tmp,'wrapper_module_0.c'),os.path.join(tmp,name+'.c'))
    os.rename(os.path.join(tmp,'wrapper_module_0.pyx'),os.path.join(tmp,name+'.pyx'))
    search_text = "wrapper_module_0"
    replace_text = name
    with open(os.path.join(tmp,name+'.c'), 'r',encoding='UTF-8') as file:
        data = file.read()
        data = data.replace(search_text, replace_text)
    with open(os.path.join(tmp,name+'.c'), 'w',encoding='UTF-8') as file:
        file.write(data)

if __name__=='__main__':
    generate_code()