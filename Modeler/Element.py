# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:17:28 2016

@author: HZJ
"""
import uuid

import numpy as np
import scipy as sp

from . import CoordinateSystem,Section
from . import config

class Element(object):
    def __init__(self,name=None):
        self.__name=uuid.uuid1() if name==None else name
        self.__hid=None #hidden id
        
    @property
    def name(self):
        return self.__name
        
    @property
    def hid(self):
        return self.__hid
    @hid.setter
    def hid(self,hid):
        self.__hid=hid
        
    @property
    def nodes(self):
        return self.__nodes
        
    @property
    def Ke(self):
        """
        element stiffness matrix.
        """
        return self.__Kij

    @property
    def Me(self):
        """
        element mass matrix.
        """
        return self.__Mij
    
    @property
    def T(self):
        """
        element local-global csys transform matrix.
        """
        T=np.zeros((12,12))
        V=self.local_csys.transform_matrix
        T[:3,:3] =T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]= V
        return T
                
class Beam(Element):
    def __init__(self,node_i, node_j, E, mu, A, I2, I3, J, rho, name=None):
        r"""
        node_i,node_j: ends of beam.
        E: elastic modulus
        mu: Possion ratio        
        A: section area
        I2: inertia about 2-2
        I3: inertia about 3-3
        J: torsianl constant
        rho: mass density
        """
        Element.__init__(self,name)
        self.__nodes=[node_i,node_j]

        #Initialize local CSys
        o = [ node_i.x, node_i.y, node_i.z ]
        pt1 = [ node_j.x, node_j.y, node_j.z ]
        pt2 = [ node_i.x, node_i.y, node_i.z ]
        if abs(node_i.x - node_j.x) < config['TOL'] and abs(node_i.y - node_j.y) < config['TOL']:
            pt2[0] += 1
        else:
            pt2[2] += 1
        self.local_csys = CoordinateSystem.cartisian(o, pt1, pt2)
        
        l=self.length
        G=E/2/(1+mu)

        #Initialize local stiffness matrix
        self.__Kij = np.zeros((12, 12))
        self.__Mij = np.zeros((12, 12))
        self.__Mij_=np.zeros((12,12))
        #form the stiffness matrix:
        self.__Kij[0, 0]=E*A / l
        self.__Kij[0, 6]=self.__Kij[6, 0]=-E*A / l

        self.__Kij[1, 1]=12 * E*I3 / l / l / l
        self.__Kij[1, 5]=self.__Kij[5, 1]=6 * E*I3 / l / l
        self.__Kij[1, 7]=self.__Kij[7, 1]=-12 * E*I3 / l / l / l
        self.__Kij[1, 11]=self.__Kij[11, 1]=6 * E*I3 / l / l

        self.__Kij[2, 2]=12 * E*I2 / l / l / l
        self.__Kij[2, 4]=self.__Kij[4, 2]=-6 * E*I2 / l / l
        self.__Kij[2, 8]=self.__Kij[8, 2]=-12 * E*I2 / l / l / l
        self.__Kij[2, 10]=self.__Kij[10, 2]=-6 * E*I2 / l / l

        self.__Kij[3, 3]=G*J / l
        self.__Kij[3, 9]=self.__Kij[9, 3]=-G*J / l

        self.__Kij[4, 4]=4 * E*I2 / l
        self.__Kij[4, 8]=self.__Kij[8, 4]=6 * E*I2 / l / l
        self.__Kij[4, 10]=self.__Kij[10, 4]=2 * E*I2 / l

        self.__Kij[5, 5]=4 * E*I3 / l
        self.__Kij[5, 7]=self.__Kij[7, 5]=-6 * E*I3 / l / l
        self.__Kij[5, 11]=self.__Kij[11, 5]=2 * E*I3 / l

        self.__Kij[6, 6]=E*A / l

        self.__Kij[7, 7]=12 * E*I3 / l / l / l
        self.__Kij[7, 11]=self.__Kij[11, 7]=-6 * E*I3 / l / l

        self.__Kij[8, 8]=12 * E*I2 / l / l / l
        self.__Kij[8, 10]=self.__Kij[10, 8]=6 * E*I2 / l / l

        self.__Kij[9, 9]=G*J / l

        self.__Kij[10, 10]=4 * E*I2 / l

        self.__Kij[11, 11]=4 * E*I3 / l

        #form mass matrix    
        #Coordinated mass matrix
        self.__Mij_[0, 0]=140
        self.__Mij_[0, 6]=70

        self.__Mij_[1, 1]=156
        self.__Mij_[1, 5]=self.__Mij_[5, 1]=22 * l
        self.__Mij_[1, 7]=self.__Mij_[7, 1]=54
        self.__Mij_[1, 11]=self.__Mij_[11, 1]=-13 * l

        self.__Mij_[2, 2]=156
        self.__Mij_[2, 4]=self.__Mij_[4, 2]=-22 * l
        self.__Mij_[2, 8]=self.__Mij_[8, 2]=54
        self.__Mij_[2, 10]=self.__Mij_[10, 2]=13 * l

        self.__Mij_[3, 3]=140 * J / A
        self.__Mij_[3, 9]=self.__Mij_[9, 3]=70 * J / A

        self.__Mij_[4, 4]=4 * l *l
        self.__Mij_[4, 8]=self.__Mij_[8, 4]=-13 * l
        self.__Mij_[4, 10]=self.__Mij_[10, 4]=-3 * l*l

        self.__Mij_[5, 5]=4 * l*l
        self.__Mij_[5, 7]=self.__Mij_[7, 5]=13 * l
        self.__Mij_[5, 11]=self.__Mij_[11, 5]=-3 * l*l

        self.__Mij_[6, 6]=140

        self.__Mij_[7, 7]=156
        self.__Mij_[7, 11]=self.__Mij_[11, 7]=-22 * l

        self.__Mij_[8, 8]=156
        self.__Mij_[8, 10]=self.__Mij_[10, 8]=22 * l

        self.__Mij_[9, 9]=140 * J / A

        self.__Mij_[10, 10]=4 * l*l

        self.__Mij_[11, 11]=4 * l*l

        self.__Mij_*= (rho*A*l / 420)

        #Concentrated mass matrix
        for i in range(12):
            self.__Mij[i, i]=1
        self.__Mij*=rho*A*l/2
        
    @property
    def nodes(self):
        return self.__nodes
    
    @property
    def length(self):
        nodeI=self.__nodes[0]
        nodeJ=self.__nodes[1]
        return np.sqrt((nodeI.x - nodeJ.x)*(nodeI.x - nodeJ.x) + (nodeI.y - nodeJ.y)*(nodeI.y - nodeJ.y) + (nodeI.z - nodeJ.z)*(nodeI.z - nodeJ.z))
    
    @property
    def Ke(self):
        return self.__Kij
    
    @property
    def Me(self):
        return self.__Mij

        
    def initialize_csys(self):
        node_i=self.__nodes[0]
        node_j=self.__nodes[1]
        o = np.array([node_i.x, node_i.y, node_i.z])
        pt1 = np.array([node_j.x, node_j.y, node_j.z])
        pt2 = np.array([0,0,0])
        if node_i.x != node_j.x and node_i.y != node_j.y:
            pt2[2] = 1
        else:
            pt2[0] = 1
        self.local_csys.set_by_3pts(o, pt1, pt2)

    def static_condensation(self, coor_mass=False):
        """
        kij_bar: 12x12 matrix
        rij_bar: 12x1 vector
        mij_bar: 12x12 matrix
        """
        kij=self.__Kij
        mij=self.__Mij
        rij=self.nodal_force
        kij_bar = kij
        mij_bar = mij
        rij_bar = rij

        for n in range(0,6):
            if self.releaseI[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_bar[i, j] = kij[i, j] - kij[i, n]* kij[n, j] / kij[n, n]
                        mij_bar[i, j] = mij[i, j] - mij[i, n]* mij[n, j] / mij[n, n]
                    rij_bar[i] = rij[i] - rij[n] * kij[n, i] / kij[n, n]
            if self.releaseJ[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_bar[i, j] = kij[i, j] - kij[i, n + 6]* kij[n + 6, j] / kij[n + 6, n + 6]
                        mij_bar[i, j] = mij[i, j] - mij[i, n + 6]* mij[n + 6, j] / mij[n + 6, n + 6]
                    rij_bar[i] = rij[i] - rij[n + 6] * kij[n + 6, i] / kij[n + 6, n + 6]
        return kij_bar, mij_bar, rij_bar

class TriMembrane(Element):
    def __init__(self,node_i, node_j, node_k, t, E, mu, rho, name=None):
        r"""
        node_i,node_j,node_k: corners of triangle.
        t: thickness
        E: elastic modulus
        mu: Poisson ratio
        rho: mass density
        """
        Element.__init__(self)
        self.__nodes=[node_i,node_j,node_k]
        self.__x0=np.array([(node.x,node.y) for node in self.__nodes])
        self.area=0.5*np.linalg.det(np.array([[1,1,1],
                                         [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                         [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))
        self.__t=t
        self.__E=E
        self.__mu=mu
        self.__rho=rho

    @property
    def section(self):
        return self.__sec
        
    def abc(self,j,m):
        """
        conversion constant.
        """
        x,y=self.__x0[:,0],self.__x0[:,1]
        a=x[j]*y[m]-x[m]*y[j]
        b=y[j]-y[m]
        c=-x[j]+x[m]
        return np.array([a,b,c])

    def N(self,x):
        """
        interpolate function.
        return: 3x1 array represent x,y
        """
        return self.L(x)
        
    def L(self,x):
        """
        convert csys from x to L
        return: 3x1 array represent x,y
        """
        x,y=x[0],x[1]
        L=np.array((3,1))
        L[0]=self.abc(1,2).dot(np.array([1,x,y]))/2/self.area
        L[1]=self.abc(2,0).dot(np.array([1,x,y]))/2/self.area
        L[2]=self.abc(0,1).dot(np.array([1,x,y]))/2/self.area
        return L.reshape(3,1)
    
    def x(self,L):
        """
        convert csys from L to x
        return: 2x1 array represent x,y
        """
        return np.dot(np.array(L).reshape(1,3),self.x0).reshape(2,1)

    def B(self,x):
        """
        strain matrix, which is derivative of intepolate function
        """
        abc0=self.abc(1,2)
        abc1=self.abc(2,0)
        abc2=self.abc(0,1)
        B0= np.array([[abc0[1],      0],
                      [      0,abc0[2]],
                      [abc0[2],abc0[1]]])
        B1= np.array([[abc1[1],     0],
                      [      0,abc1[2]],
                      [abc1[2],abc1[1]]])
        B2= np.array([[abc2[1],      0],
                      [      0,abc2[2]],
                      [abc2[2],abc2[1]]])
        return np.hstack([B0,B1,B2])/2/self.area
    
    def S(self,x):
        """
        stress matrix
        """
        return np.dot(self.D,self.B(x))
                                 
    @property  
    def Ke(self):
        """
        integrate to get stiffness matrix.
        """
        E=self.__E
        mu=self.__mu
        D0=E/(1-mu**2)
        D=np.array([[1,mu,0],
                    [mu,1,0],
                    [0,0,(1-mu)/2]])*D0
        res=np.dot(np.dot(self.B(0).T,D),self.B(0))*self.area*self.__t               
        return res
        
class TriPlate(Element):
    def __init__(self,node_i, node_j, node_k, sec ,name=None):
        Element.__init__(self)
        self.nodes=[node_i,node_j,node_k]
        self.x0=np.array([(node.x,node.y) for node in self.nodes])
        self.area=0.5*np.linalg.det(np.array([[1,1,1],
                                         [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                         [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))
        self.t=sec.t
        self.__sec=sec

    @property
    def section(self):
        return self.__sec
        
    def abc(self,j,m):
        """
        conversion constant.
        """
        x,y=self.x0[:,0],self.x0[:,1]
        a=x[j]*y[m]-x[m]*y[j]
        b=y[j]-y[m]
        c=-x[j]+x[m]
        return np.array([a,b,c])

    def N(self,x):
        """
        interpolate function.
        return: 3x1 array represent x,y
        """
        return self.L(x)
        
    def N_(self,x):
        """
        reversed interpolate function.
        return: 3x1 array represent x,y
        """
        return self.x0.T
        
    def L(self,x):
        """
        convert csys from x to L
        return: 3x1 array represent x,y
        """
        x,y=x[0],x[1]
        L=np.array((3,1))
        L[0]=self.abc(1,2).dot(np.array([1,x,y]))/2/self.area
        L[1]=self.abc(2,0).dot(np.array([1,x,y]))/2/self.area
        L[2]=self.abc(0,1).dot(np.array([1,x,y]))/2/self.area
        return L.reshape(3,1)
    
    def x(self,L):
        """
        convert csys from L to x
        return: 2x1 array represent x,y
        """
        return np.dot(np.array(L).reshape(1,3),self.x0).reshape(2,1)

    def B(self,x):
        """
        strain matrix, which is derivative of intepolate function
        """
        abc0=self.abc(1,2)
        abc1=self.abc(2,0)
        abc2=self.abc(0,1)
        B0= np.array([[abc0[1],      0],
                      [      0,abc0[2]],
                      [abc0[2],abc0[1]]])
        B1= np.array([[abc1[1],     0],
                      [      0,abc1[2]],
                      [abc1[2],abc1[1]]])
        B2= np.array([[abc2[1],      0],
                      [      0,abc2[2]],
                      [abc2[2],abc2[1]]])
        return np.hstack([B0,B1,B2])/2/self.area
    
    def S(self,x):
        """
        stress matrix
        """
        return np.dot(self.D,self.B(x))
    
    @property  
    def J(self):
        """
        Jacobi matrix
        """
        dxdL1=self.x0[0,0]
        dxdL2=self.x0[1,0]
        dydL1=self.x0[0,1]
        dydL2=self.x0[1,1]
        return np.array([[dxdL1,dydL1],
                        [dxdL2,dydL2]])
                               
    @property  
    def K(self):
        """
        integrate to get stiffness matrix.
        """
        E=self.__sec.material.E
        mu=self.__sec.material.mu
        D0=E/(1-mu**2)
        D=np.array([[1,mu,0],
                    [mu,1,0],
                    [0,0,(1-mu)/2]])*D0
#        res=np.zeros((6,6))
#        def gfunc(x):
#            return 0
#        def hfunc(x):
#            return 1-x
        res=np.dot(np.dot(self.B(0).T,D),self.B(0))*self.area*self.t
#        for i in range(6):
#            for j in range(6):
#                res[i,j]=sp.integrate.dblquad(lambda x,y:A[i,j],0,1,gfunc,hfunc)[0]*self.t                 
        return res
    
class IsoParametric(Element):
    def __init__(self,dim,name=None):
        Element.__init__(self)
        self.dim=dim
        self.A=np.array()
        self.B=self.A.T
        self.N
        self.x=np.array()
        self.E        
        self.nodes=[]
        
    #interpolate function
    def N(s):
        pass
    
    #strain matrix
    def B(self,s):
        pass
    
    #stress matrix
    def S(self,s):
        return np.dot(self.D,self.B(s))
    
    #csys transformation
    def x(self,s):
        """
        s: DIMx1 vector
        """
        n=self.dim*len(self.nodes)
        x0=np.array([(node.x,node.y,node.z) for node in self.nodes]).reshape((n,1))
        N=np.hstack([(np.eye(self.dim)*Ni) for Ni in self.N(s)]) #DIMx3*DIM matrix
        return np.dot(N,x0)
        
    def d(self,s,u):
        """
        compute strain with local coordinate s and displacement u.
        s: 
        """
        return np.dot(B(s),self.u)
        
    def K_(self):
        def f(s):
            return np.dot(np.dot(np.dot(self.B(s).T,self.E),self.B(s)),self.J(s))
        return sp.integrate.quad(f,-1,1)
        
    def K(self):
        return np.dot(np.dot(self.G.T,self.P),self.G)
    
    def P(self):
        return np.dot(self.G.T,self.P)
        
class Plate(IsoParametric):
    def __init__(self,sec,node_i, node_j, node_k, node_l, name=None):
        #8-nodes
        self.__nodes.append(node_i)
        self.__nodes.append(node_j)
        self.__nodes.append(node_k)
        self.__nodes.append(node_l)
        self.__nodes.append((node_i+node_j)/2)
        self.__nodes.append((node_j+node_k)/2)
        self.__nodes.append((node_k+node_l)/2)
        self.__nodes.append((node_l+node_i)/2)

        self.load_i=[0]*6
        self.load_j=[0]*6
        self.load_k=[0]*6
        self.load_l=[0]*6
        
        self.__section=sec
        self.__rotation=0
        
        self.__load_d=[]
        self.__load_c=[]
        self.__load_s=[]
        self.__load_t=[]
        
        center=np.mean([node_i,node_j,node_k,node_l])
#        self.local_csys = CoordinateSystem.cartisian(center,nodes[4],nodes[5])
        
        self.__alpha=[]#the angle between edge and local-x, to be added
        self.__alpha.append(self.angle(node_i,node_j,self.local_csys.x))
        self.__alpha.append(self.angle(node_j,node_k,self.local_csys.x))
        self.__alpha.append(self.angle(node_k,node_l,self.local_csys.x))
        self.__alpha.append(self.angle(node_l,node_i,self.local_csys.x))

        self.__K=np.zeros((24,24))

    #interpolate function in r-s csys
    def __N(s):
        r,s=s[0],s=[1]
        N=[]
        N.append((1-r)*(1-s)/4)
        N.append((1+r)*(1-s)/4)
        N.append((1+r)*(1+s)/4)
        N.append((1-r)*(1+s)/4)
        N.append((1-r**2)*(1-s)/2)
        N.append((1+r)*(1-s**2)/2)
        N.append((1-r**2)*(1+s)/2)
        N.append((1-r)*(1-s**2)/2)
        return np.array(N)

        
    def B(s):
        pass
                            
    def angle(node_i,node_j,x):
        v=np.array([node_j.X-node_i.X,node_j.Y-node_i.Y,node_j.Z-node_i.Z])
        L1=np.sqrt(v.dot(v))
        L2=np.sqrt(x.dot(x))
        return np.arccos(v.dot(x)/L1/L2)

        #derivation
    def __dNds(s):
        r,s=s[0],s=[1]
        dNdr=[-(1-s)/4]
        dNdr.append((1-s)/4)
        dNdr.append((1+s)/4)
        dNdr.append(-(1+s)/4)
        dNdr.append(-(1-s)*r)
        dNdr.append((1-s*s)/2)
        dNdr.append(-(1+s)*r)
        dNdr.append(-(1-s*s)/2)
      
        dNds=[-(1-r)/4]
        dNds.append(-(1+r)/4)
        dNds.append((1+r)/4)
        dNds.append((1-r)/4)
        dNds.append(-(1-r*r)/2)
        dNds.append(-(1+r)*s)
        dNds.append((1+r*r)/2)
        dNds.append(-(1-r)*s)
        return np.array([dNdr,dNds])
        
        #Jacobi matrix
    def __J(self,x,s):
        x,y=x[0],x=[1]
        dxdr=np.sum(self.__dNds(s)[0]*x)
        dydr=np.sum(self.__dNds(s)[0]*y)
        dxds=np.sum(self.__dNds(s)[1]*x)
        dyds=np.sum(self.__dNds(s)[1]*y)
        J=[[dxdr,dydr],
           [dxds,dyds]]
        return J 
        
    def dxds():      
        pass
        
#    def dNdx(self,x):
#        dNdx=[]
#        dNdy=[]
#        for i in range(8): 
#            dNdx.append(self.__dNdr[i]/dxds(r)+self.__dNds[i]/dxds)
#            dNdy.append(self.__dNdr[i]/dyds(r)+self.__dNds[i]/dyds)
        
    def __dMds(self,s):
        r,s=s[0],s[1]
        N=self.__N(r,s)
        alpha=self.__alpha()
        Mx=[]
        Mx.append(N[4]*np.sin(alpha[0]))
        Mx.append(N[5]*np.sin(alpha[1]))
        Mx.append(N[6]*np.sin(alpha[2]))
        Mx.append(N[7]*np.sin(alpha[3]))
        #derivation
        dMxdr=[]
        dMxdr.append(-(1-s)*r)*np.sin(alpha[0])
        dMxdr.append((1-s*s)/2)*np.sin(alpha[1])
        dMxdr.append(-(1+s)*r)*np.sin(alpha[2])
        dMxdr.append(-(1-s*s)/2)*np.sin(alpha[3])
        
        My=[]
        My.append(-N[4]*np.cos(alpha[0]))
        My.append(-N[5]*np.cos(alpha[1]))
        My.append(-N[6]*np.cos(alpha[2]))
        My.append(-N[7]*np.cos(alpha[3]))
        dMydr=[]
        dMydr.append((1-s)*r)*np.cos(alpha[0])
        dMydr.append(-(1-s*s)/2)*np.cos(alpha[1])
        dMydr.append((1+s)*r)*np.cos(alpha[2])
        dMydr.append((1-s*s)/2)*np.cos(alpha[3])
      
        dMxds=[]
        dMxds.append(-(1-r)/4*np.sin(alpha[0]))
        dMxds.append(-(1+r)/4*np.sin(alpha[1]))
        dMxds.append((1+r)/4*np.sin(alpha[2]))
        dMxds.append((1-r)/4*np.sin(alpha[3]))
        dMyds=[]
        dMyds.append((1-r*r)/2*np.cos(alpha[0]))
        dMyds.append((1+r)*s*np.cos(alpha[1]))
        dMyds.append(-(1+r*r)/2*np.cos(alpha[2]))
        dMyds.append((1-r)*s*np.cos(alpha[3]))
        
        dMxdr=np.array(dMxdr)
        dMydr=np.array(dMxdr)
        dMxds=np.array(dMyds)
        dMyds=np.array(dMyds)
        return [[dMxdr,dMydr],
                [dMxds,dMyds]]
         
#    def __dMdx(self,r):
#        #dx/dr=1/(dr/dx)?
#        dMxdx=[]
#        dMxdy=[]
#        dMydx=[]
#        dMydy=[]
#        dMxdr,dMydr,dMxds,dMyds=self.dMdr(r)
#        for i in range(4): 
#            dMxdx.append(dMxdr[i]/dxdr+dMxds[i]/dxds)
#            dMxdy.append(dMxdr[i]/dxdr+dMxds[i]/dyds)
#            dMydx.append(dMydr[i]/dxdr+dMyds[i]/dxds)
#            dMydy.append(dMydr[i]/dydr+dMyds[i]/dyds)
#        return (dMxdy,dMxdy,dMydx,dMydy)
        
        D=[np.cos(alpha[0])*np.sin(alpha[3])-np.sin(alpha[0])*np.cos(alpha[3]),
           np.cos(alpha[1])*np.sin(alpha[0])-np.sin(alpha[1])*np.cos(alpha[0]),
           np.cos(alpha[2])*np.sin(alpha[1])-np.sin(alpha[2])*np.cos(alpha[1]),
           np.cos(alpha[3])*np.sin(alpha[2])-np.sin(alpha[3])*np.cos(alpha[2])]
#        
#        b=[[       0,       0,       0,       0,dNdx[0],dNdx[1],dNdx[2],dNdx[3],0,0,0,0,        dMydx[0],        dMydx[1],        dMydx[2],        dMydx[3]],
#           [ dNdy[0], dNdy[1], dNdy[2], dNdy[3],      0,      0,      0,      0,0,0,0,0,        dMxdy[0],        dMxdy[1],        dMxdy[2],        dMxdy[3]],
#           [-dNdx[0],-dNdx[1],-dNdx[2],-dNdx[3],dNdy[0],dNdy[1],dNdy[2],dNdy[3],0,0,0,0,dMydy[0]-dMxdx[0],dMydy[1]-dMxdx[1],dMydy[2]-dMxdx[2],dMydy[3]-dMxdx[3]],
#           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
#           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
#           
#        for i in range(4):
#            gamma_e[i]=1/L()
#           
##        detJ=J[1,1]*J[2,2]-J[1,2]*J[2,1]
##        
##        a=[[z,0,0,0,0],
##           [0,z,0,0,0],
##           [0,0,z,0,0],
##           [0,0,0,1,0],
##           [0,0,0,0,1]]
##           
##        gamma=np.zeros((4,4))
##        for i in range(4):
##            for j in range(4):
##                gamma[i,j]=1/L*()
##      
##        
##        M1dx,M2dx,M3dx,M4dx=N1dy,N2dy,N3dy,N4dy
##        M1dy,M2dy,M3dy,M4dy=N1dy,N2dy,N3dy,N4dy
##        
##        if sec.Material.type=='Iso':
##            D11=D22=E*h**3/(12*(1-mu**2))
##            D12=D21=mu*E*h**3/(12*(1-mu**2))
##            D44=D55=5*E*h**3/(12*(1+mu))
##            D=[[D11,D12,0,  0,  0],
##               [D21,D22,0,  0,  0],
##               [  0,  0,0,  0,  0],
##               [  0,  0,0,D44,  0],
##               [  0,  0,0,  0,D55]]
##
##           
##        k=sp.integrate.dblquad(
##                       func,-1,1
##                       )
##           
##        
##        #Calculate edge shear
##        alpha[0,1]=-alpha[1,0]
##        alpha[1,2]=-alpha[2,1]
##        alpha[2,3]=-alpha[3,2]
##        alpha[3,0]=-alpha[0,3]
##        
##        gamma_e=[]
##        for i in range(4):
##            gamma.append()
#        
#    def membrane_to_integrate(self,r,s):
#        """
#        bT-D-b
#        """
#        alpha=[]
#        for i in range(4):
#            alpha.append("the angle between edge i and x")
#        
#        #derivation
#        dNdr=[-(1-s)/4]
#        dNdr.append((1-s)/4)
#        dNdr.append((1+s)/4)
#        dNdr.append(-(1+s)/4)
#        dNdr.append(-(1-s)*r)
#        dNdr.append((1-s*s)/2)
#        dNdr.append(-(1+s)*r)
#        dNdr.append(-(1-s*s)/2)
#        
#        dNds=[-(1-r)/4]
#        dNds.append(-(1+r)/4)
#        dNds.append((1+r)/4)
#        dNds.append((1-r)/4)
#        dNds.append(-(1-r*r)/2)
#        dNds.append(-(1+r)*s)
#        dNds.append((1+r*r)/2)
#        dNds.append(-(1-r)*s)
#        
#        dNdr=np.array(dNdr)
#        dNds=np.array(dNds)
#        
#        #Jacobi matrix
#        dxdr=sum(dNdr*x)
#        dydr=sum(dNdr*y)
#        dxds=sum(dNds*x)
#        dyds=sum(dNds*y)
#        J=[[dxdr,dydr],
#           [dxds,dyds]]
#        
#        #dx/dr=1/(dr/dx)?
#        dNdx=[]
#        dNdy=[]
#        for i in range(8): 
#            dNdx.append(dNdr[i]/dxdr+dNds[i]/dxds)
#            dNdy.append(dNdr[i]/dydr+dNds[i]/dyds)
#            
#        N=self.__N
#        Mx=[]
#        Mx.append(N[4]*np.sin(alpha[0]))
#        Mx.append(N[5]*np.sin(alpha[1]))
#        Mx.append(N[6]*np.sin(alpha[2]))
#        Mx.append(N[7]*np.sin(alpha[3]))
#        My=[]
#        My.append(-N[4]*np.cos(alpha[0]))
#        My.append(-N[5]*np.cos(alpha[1]))
#        My.append(-N[6]*np.cos(alpha[2]))
#        My.append(-N[7]*np.cos(alpha[3]))
#        
#        #derivation
#        dMxdr=[]
#        dMxdr.append(-(1-s)*r)*np.sin(alpha[0])
#        dMxdr.append((1-s*s)/2)*np.sin(alpha[1])
#        dMxdr.append(-(1+s)*r)*np.sin(alpha[2])
#        dMxdr.append(-(1-s*s)/2)*np.sin(alpha[3])
#        dMydr=[]
#        dMydr.append((1-s)*r)*np.cos(alpha[0])
#        dMydr.append(-(1-s*s)/2)*np.cos(alpha[1])
#        dMydr.append((1+s)*r)*np.cos(alpha[2])
#        dMydr.append((1-s*s)/2)*np.cos(alpha[3])
#        
#        dMxds=[]
#        dMxds.append(-(1-r)/4*np.sin(alpha[0]))
#        dMxds.append(-(1+r)/4*np.sin(alpha[1]))
#        dMxds.append((1+r)/4*np.sin(alpha[2]))
#        dMxds.append((1-r)/4*np.sin(alpha[3]))
#        dMyds=[]
#        dMyds.append((1-r*r)/2*np.cos(alpha[0]))
#        dMyds.append((1+r)*s*np.cos(alpha[1]))
#        dMyds.append(-(1+r*r)/2*np.cos(alpha[2]))
#        dMyds.append((1-r)*s*np.cos(alpha[3]))
#        
#        dMxdr=np.array(dMxdr)
#        dMydr=np.array(dMxdr)
#        dMxds=np.array(dMyds)
#        dMyds=np.array(dMyds)
#                
#        #dx/dr=1/(dr/dx)?
#        dMxdx=[]
#        dMxdy=[]
#        dMydx=[]
#        dMydy=[]
#        for i in range(4): 
#            dMxdx.append(dMxdr[i]/dxdr+dMxds[i]/dxds)
#            dMxdy.append(dMxdr[i]/dxdr+dMxds[i]/dyds)
#            dMydx.append(dMydr[i]/dxdr+dMyds[i]/dxds)
#            dMydy.append(dMydr[i]/dydr+dMyds[i]/dyds)
#        
#        B=[[ dNdx[0],dNdx[1],dNdx[2],dNdx[3],      0,      0,      0,      0,         dMxdx[0],         dMxdx[1],         dMxdx[2],         dMxdx[3]],
#           [       0,      0,      0,      0,dNdy[0],dNdy[1],dNdy[2],dNdy[3],         dMydy[0],         dMydy[1],         dMydy[2],         dMydy[3]],
#           [ dNdx[0],dNdx[1],dNdx[2],dNdx[3],dNdy[0],dNdy[1],dNdy[2],dNdy[3],dMxdy[0]+dMydx[0],dMxdy[1]+dMydx[1],dMxdy[2]+dMydx[2],dMxdy[3]+dMydx[3]]]
#
#        return B.T.dot(D).dot(B)
#
#    
#    
#
#    def cartisian_to_area(x1,y1):    
#        a[0]=x[0]*y[2]-x[2]*y[0]
#        b[0]=y[1]-y[2]
#        c[0]=-x[1]+x[2]
#        
#        a[1]=x[1]*y[0]-x[0]*y[1]
#        b[1]=y[2]-y[0]
#        c[1]=-x[2]+x[0]
#        
#        a[2]=x[2]*y[1]-x[1]*y[2]
#        b[2]=y[0]-y[1]
#        c[2]=-x[0]+x[1]
#        
#        for i in range(3):
#            L[i]=(a[i]+b[i]*x1+c[i]*y1)
#            
#    def area_to_cartisian(L):
#        x2=0
#        y2=0
#        for i in range(3):
#            x2+=x[i]*L[i]
#            y2+=y[i]*L[i]
#            
#    L1,L2,L3=L[1],L[2],L[0]
#    a1,a2,a3=a[1],a[2],a[0]
#    b1,b2,b3=b[1],b[2],b[0]
#    c1,c2,c3=c[1],c[2],c[0]
#    
#    N[1]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
#    
#    L1,L2,L3=L[2],L[0],L[1]
#    a1,a2,a3=a[2],a[0],a[1]
#    b1,b2,b3=b[2],b[0],b[1]
#    c1,c2,c3=c[2],c[0],c[1]
#    
#    N[2]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
#    
#    L1,L2,L3=L[0],L[1],L[2]
#    a1,a2,a3=a[0],a[1],a[2]
#    b1,b2,b3=b[0],b[1],b[2]
#    c1,c2,c3=c[0],c[1],c[2]
#    
#    N[0]=[
#    L1+L1**2*L2+L1**2*L3-L1*L2**2-L1*L3**2,
#    b2*(L3*L1**2+L1*L2*L3/2)-b3*(L1**2*L2+L1*L2*L3/2),
#    c2*(L3*L1**2+L1*L2*L3/2)-c3*(L1**2*L2+L1*L2*L3/2)
#    ]
    
        
#if __name__=='__main__':
#    import Node
#    import Material
#    import Section
#    m = Material.material(2.000E11, 0.3, 7849.0474, 1.17e-5)
#    s = Section.section(m, 4.800E-3, 1.537E-7, 3.196E-5, 5.640E-6)
#    n1=Node.node(1,2,3)
#    n2=Node.node(2,3,4)
#    b=beam(n1,n2,s)