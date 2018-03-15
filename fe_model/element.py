# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 22:17:28 2016

@author: HZJ
"""
import uuid

import numpy as np
import scipy as sp
import scipy.sparse as spr
import quadpy

from csys import Cartisian

class Element(object):
    def __init__(self,dim,dof,name=None):
        self._name=uuid.uuid1() if name==None else name
        self._hid=None #hidden id
        
        self._dim=dim
        self._dof=dof
               
    @property
    def name(self):
        return self._name
        
    @property
    def hid(self):
        return self._hid
    @hid.setter
    def hid(self,hid):
        self._hid=hid
        
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def node_count(self):
        return len(self._nodes)
    
    @property  
    def Ke(self):
        """
        integrate to get stiffness matrix.
        """
        return self._Ke
        
    @property  
    def Me(self):
        """
        integrate to get stiffness matrix.
        """
        return self._Me
        
    @property
    def re(self):
        return self._re
    
    @re.setter
    def re(self,force):
        if len(force)!=self._dof:
            raise ValueError('element nodal force must be a 12 array')
        self.__re=np.array(force).reshape((self._dof,1))
        
    @property
    def transform_matrix(self):
        T=np.zeros((self.node_count*6,self.node_count*6))
        V=self.local_csys.transform_matrix
        for i in range(self._dof):
            T[i*3:i*3+3,i*3:i*3+3]=V
        return T

                
class Beam(Element):
    def __init__(self,node_i, node_j, E, mu, A, I2, I3, J, rho, name=None, mass='conc', tol=1e-6):
        """
        params:
            node_i,node_j: ends of beam.
            E: elastic modulus
            mu: Possion ratio        
            A: section area
            I2: inertia about 2-2
            I3: inertia about 3-3
            J: torsianl constant
            rho: mass density
            mass: 'coor' as coordinate matrix or 'conc' for concentrated matrix
            tol: tolerance
        """
        super(Beam,self).__init__(1,6,name)
        self._nodes=[node_i,node_j]
        self._releases=[[False,False,False,False,False,False],
                         [False,False,False,False,False,False]]
        
        #Initialize local CSys
        o = [ node_i.x, node_i.y, node_i.z ]
        pt1 = [ node_j.x, node_j.y, node_j.z ]
        pt2 = [ node_i.x, node_i.y, node_i.z ]
        if abs(node_i.x - node_j.x) < tol and abs(node_i.y - node_j.y) < tol:
            pt2[0] += 1
        else:
            pt2[2] += 1
        self.local_csys = Cartisian(o, pt1, pt2)
        
        self._length=((node_i.x - node_j.x)**2 + (node_i.y - node_j.y)**2 + (node_i.z - node_j.z)**2)**0.5
        self._mass=rho*A*self.length
        
        l=self.length
        G=E/2/(1+mu)

        #Initialize local stiffness matrix
        self._Ke = np.zeros((12, 12))
        self._Me = np.zeros((12, 12))
        self._re =np.zeros((12,1))
        #form the stiffness matrix:
        self._Ke[0, 0]=E*A / l
        self._Ke[0, 6]=self._Ke[6, 0]=-E*A / l

        self._Ke[1, 1]=12 * E*I3 / l / l / l
        self._Ke[1, 5]=self._Ke[5, 1]=6 * E*I3 / l / l
        self._Ke[1, 7]=self._Ke[7, 1]=-12 * E*I3 / l / l / l
        self._Ke[1, 11]=self._Ke[11, 1]=6 * E*I3 / l / l

        self._Ke[2, 2]=12 * E*I2 / l / l / l
        self._Ke[2, 4]=self._Ke[4, 2]=-6 * E*I2 / l / l
        self._Ke[2, 8]=self._Ke[8, 2]=-12 * E*I2 / l / l / l
        self._Ke[2, 10]=self._Ke[10, 2]=-6 * E*I2 / l / l

        self._Ke[3, 3]=G*J / l
        self._Ke[3, 9]=self._Ke[9, 3]=-G*J / l

        self._Ke[4, 4]=4 * E*I2 / l
        self._Ke[4, 8]=self._Ke[8, 4]=6 * E*I2 / l / l
        self._Ke[4, 10]=self._Ke[10, 4]=2 * E*I2 / l

        self._Ke[5, 5]=4 * E*I3 / l
        self._Ke[5, 7]=self._Ke[7, 5]=-6 * E*I3 / l / l
        self._Ke[5, 11]=self._Ke[11, 5]=2 * E*I3 / l

        self._Ke[6, 6]=E*A / l

        self._Ke[7, 7]=12 * E*I3 / l / l / l
        self._Ke[7, 11]=self._Ke[11, 7]=-6 * E*I3 / l / l

        self._Ke[8, 8]=12 * E*I2 / l / l / l
        self._Ke[8, 10]=self._Ke[10, 8]=6 * E*I2 / l / l

        self._Ke[9, 9]=G*J / l

        self._Ke[10, 10]=4 * E*I2 / l

        self._Ke[11, 11]=4 * E*I3 / l

        #form mass matrix
        if mass=='coor':#Coordinated mass matrix
            self._Me[0, 0]=140
            self._Me[0, 6]=70
    
            self._Me[1, 1]=156
            self._Me[1, 5]=self._Me_[5, 1]=22 * l
            self._Me[1, 7]=self._Me_[7, 1]=54
            self._Me[1, 11]=self._Me_[11, 1]=-13 * l
    
            self._Me[2, 2]=156
            self._Me[2, 4]=self._Me_[4, 2]=-22 * l
            self._Me[2, 8]=self._Me_[8, 2]=54
            self._Me[2, 10]=self._Me_[10, 2]=13 * l
    
            self._Me[3, 3]=140 * J / A
            self._Me[3, 9]=self._Me_[9, 3]=70 * J / A
    
            self._Me[4, 4]=4 * l *l
            self._Me[4, 8]=self._Me_[8, 4]=-13 * l
            self._Me[4, 10]=self._Me_[10, 4]=-3 * l*l
    
            self._Me[5, 5]=4 * l*l
            self._Me[5, 7]=self._Me_[7, 5]=13 * l
            self._Me[5, 11]=self._Me_[11, 5]=-3 * l*l
    
            self._Me[6, 6]=140
    
            self._Me[7, 7]=156
            self._Me[7, 11]=self._Me_[11, 7]=-22 * l
    
            self._Me[8, 8]=156
            self._Me[8, 10]=self._Me_[10, 8]=22 * l
    
            self._Me[9, 9]=140 * J / A
    
            self._Me[10, 10]=4 * l*l
    
            self._Me[11, 11]=4 * l*l
    
            self._Me*= (rho*A*l / 420)
        
        if mass=='conc':#Concentrated mass matrix
            self._Me=np.eye(12)*rho*A*l/2
            
        self._Ke_=self._Ke
        self._Me_=self._Me
    
    @property
    def length(self):
        return self._length
        
    @property
    def mass(self):
        return self._mass
    
    @property
    def Ke_(self):
        return self._Ke_
    
    @property
    def Me_(self):
        return self._Me_
    
    @property    
    def re_(self):
        return self._re_
    
    @property
    def releases(self):
        return self._releases
    
    @releases.setter
    def releases(self,rls):
        if len(rls)!=12:
            raise ValueError('rls must be a 12 boolean array')
        self._releases=np.array(rls).reshape((2,6))
        
    @property
    def transform_matrix(self):
        T=np.zeros((12,12))
        V=self.local_csys.transform_matrix
        T[:3,:3] =T[3:6,3:6]=T[6:9,6:9]=T[9:,9:]= V
        return T

    def static_condensation(self):
        """
        kij_bar: 12x12 matrix
        rij_bar: 12x1 vector
        mij_bar: 12x12 matrix
        """
        releaseI=self._releases[0]
        releaseJ=self._releases[1]
        kij=self._Ke
        mij=self._Me
        rij=self._re
        kij_bar = kij.copy()
        mij_bar = mij.copy()
        rij_bar = rij.copy()
        for n in range(0,6):
            if releaseI[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_bar[i, j] = kij[i, j] - kij[i, n]* kij[n, j] / kij[n, n]
                        mij_bar[i, j] = mij[i, j] - mij[i, n]* mij[n, j] / mij[n, n]
                    rij_bar[i] = rij[i] - rij[n] * kij[n, i] / kij[n, n]
            if releaseJ[n] == True:
                for i in range(12):
                    for j in range(12):
                        kij_bar[i, j] = kij[i, j] - kij[i, n + 6]* kij[n + 6, j] / kij[n + 6, n + 6]
                        mij_bar[i, j] = mij[i, j] - mij[i, n + 6]* mij[n + 6, j] / mij[n + 6, n + 6]
                    rij_bar[i] = rij[i] - rij[n + 6] * kij[n + 6, i] / kij[n + 6, n + 6]
        self._Ke_=kij_bar
        self._Me_=mij_bar
        self._re_=rij_bar
#        ##pythonic code, not finished
#        Ke=self._Ke.copy()
#        Me=self._Me.copy()
#        re=self._re.copy()
#        n_rls=0
#        i=0
#        idx=[]
#        for rls in self._releases[0]+self.releases[1]:
#            if rls:
#                n_rls+=1
#                Ke[[i,-n_rls],:]=Ke[[-n_rls,i],:]
#                Ke[:,[i,-n_rls]]=Ke[:,[-n_rls,i]]
#                Me[[i,-n_rls],:]=Me[[-n_rls,i],:]
#                Me[:,[i,-n_rls]]=Me[:,[-n_rls,i]]
#                re[[i,-n_rls],:]=re[[-n_rls,i],:]
#                idx.append(i)
#            i+=1
#
#        if n_rls==0:
#            self._Ke_,self._Me_,self._re_=Ke,Me,re
#            return 
#        n0=12-n_rls
#        Ke_=Ke[:n0,:n0]-Ke[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(Ke[n0:,:n0])
#        Me_=Me[:n0,:n0]-Me[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(Me[n0:,:n0])
#        re_=re[:n0]-Ke[:n0,n0:].dot(np.mat(Ke[n0:,n0:]).I).dot(re[:n0])
#        for i in idx:
#            Ke_=np.insert(Ke_,i,0,axis=0)
#            Ke_=np.insert(Ke_,i,0,axis=1)
#            Me_=np.insert(Me_,i,0,axis=0)
#            Me_=np.insert(Me_,i,0,axis=1)
#            re_=np.insert(re_,i,0,axis=0)
#        self._Ke_,self._Me_,self._re_=Ke_,Me_,re_
        def resolve_element_force():
            pass
                
                

class Membrane3(Element):
    def __init__(self,node_i, node_j, node_k, t, E, mu, rho, name=None):
        r"""
        node_i,node_j,node_k: corners of triangle.
        t: thickness
        E: elastic modulus
        mu: Poisson ratio
        rho: mass density
        """
        super(Membrane3,self).__init__(2,6,name)
        self._nodes=[node_i,node_j,node_k]
        self._area=0.5*np.linalg.det(np.array([[1,1,1],
                                         [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                         [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))
        self._t=t
        self._E=E
        self._mu=mu
        self._rho=rho
        
        #Initialize local CSys
        o=[(node_i.x+node_j.x+node_k.x)/3,
            (node_i.y+node_j.y+node_k.y)/3,
            (node_i.z+node_j.z+node_k.z)/3]
        pt1 = [ node_j.x, node_j.y, node_j.z ]
        pt2 = [ node_i.x, node_i.y, node_i.z ]
        self.local_csys = Cartisian(o, pt1, pt2) 
        
        x0=np.array([(node.x,node.y,node.z) for node in self._nodes])
        V=self.local_csys.transform_matrix
        self._x0=(x0-np.array(o)).dot(V.T)[:,:2]
        
        E=self._E
        mu=self._mu
        D0=E/(1-mu**2)
        D=np.array([[1,mu,0],
                    [mu,1,0],
                    [0,0,(1-mu)/2]])*D0
        _Ke_=np.dot(np.dot(self._B(0).T,D),self._B(0))*self.area*self._t

        row=[a for a in range(0*2,0*2+2)]+\
            [a for a in range(1*2,1*2+2)]+\
            [a for a in range(2*2,2*2+2)]
        col=[a for a in range(0*6,0*6+2)]+\
            [a for a in range(1*6,1*6+2)]+\
            [a for a in range(2*6,2*6+2)]
        elm_node_count=3
        elm_dof=2
        data=[1]*(elm_node_count*elm_dof)
        G=sp.sparse.csr_matrix((data,(row,col)),shape=(elm_node_count*elm_dof,elm_node_count*6))
        self._Ke=G.transpose()*_Ke_*G

        #Concentrated mass matrix, may be wrong
        self._Me=np.eye(18)*rho*self.area*t/3
        
        self._re =np.zeros((18,1))
        
    @property
    def area(self):
        return self._area
        
    def _abc(self,j,m):
        """
        conversion constant.
        """
        x,y=self._x0[:,0],self._x0[:,1]
        a=x[j]*y[m]-x[m]*y[j]
        b=y[j]-y[m]
        c=-x[j]+x[m]
        return np.array([a,b,c])

    def _N(self,x):
        """
        interpolate function.
        return: 3x1 array represent x,y
        """
        return self._L(x)
        
    def _L(self,x):
        """
        convert csys from x to L
        return: 3x1 array represent x,y
        """
        x,y=x[0],x[1]
        L=np.array((3,1))
        L[0]=self._abc(1,2).dot(np.array([1,x,y]))/2/self._area
        L[1]=self._abc(2,0).dot(np.array([1,x,y]))/2/self._area
        L[2]=self._abc(0,1).dot(np.array([1,x,y]))/2/self._area
        return L.reshape(3,1)
    
    def _x(self,L):
        """
        convert csys from L to x
        return: 2x1 array represent x,y
        """
        return np.dot(np.array(L).reshape(1,3),self._x0).reshape(2,1)

    def _B(self,x):
        """
        strain matrix, which is derivative of intepolate function
        """
        abc0=self._abc(1,2)
        abc1=self._abc(2,0)
        abc2=self._abc(0,1)
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
    
class IsoParametric(Element):
    def __init__(self,dim,dof,name=None):
        super(IsoParametric,self).__init__(dim,dof,name)
        
    #interpolate function
    def _N(s):
        pass
    
    def _J(s):
        pass
    
    #strain matrix
    def _B(self,s):
        pass
    
    #stress matrix
    def _S(self,s):
        return np.dot(self.D,self.B(s))
    
    #csys transformation
    def _x(self,s):
        """
        s: DIMx1 vector
        """
        n=self.dim*len(self.nodes)
        x0=np.array([(node.x,node.y,node.z) for node in self.nodes]).reshape((n,1))
        N=np.hstack([(np.eye(self.dim)*Ni) for Ni in self.N(s)]) #DIMx3*DIM matrix
        return np.dot(N,x0)
        
    def _d(self,s,u):
        """
        compute strain with local coordinate s and displacement u.
        s: 
        """
        return np.dot(self.__B(s),self.u)

class Membrane4(IsoParametric):
    def __init__(self,node_i, node_j, node_k, node_l, t, E, mu, rho, name=None):
        r"""
        node_i,node_j,node_k: corners of triangle.
        t: thickness
        E: elastic modulus
        mu: Poisson ratio
        rho: mass density
        """
        super(Membrane4,self).__init__(2,8,name)
        self._nodes=[node_i,node_j,node_k,node_l]
        
        self._area=0.5*sp.linalg.det(np.array([[1,1,1],
                                         [node_j.x-node_i.x,node_j.y-node_i.y,node_j.z-node_i.z],
                                         [node_k.x-node_i.x,node_k.y-node_i.y,node_k.z-node_i.z]]))
        
        self._area+=0.5*sp.linalg.det(np.array([[1,1,1],
                                         [node_l.x-node_k.x,node_l.y-node_k.y,node_l.z-node_i.z],
                                         [node_i.x-node_k.x,node_i.y-node_k.y,node_i.z-node_i.z]]))
        self._t=t
        self._E=E
        self._mu=mu
        self._rho=rho
        
        #Initialize local CSys
        o=[(node_i.x+node_j.x+node_k.x+node_l.x)/4,
            (node_i.y+node_j.y+node_k.y+node_l.y)/4,
            (node_i.z+node_j.z+node_k.z+node_l.z)/4]
        pt1 = [(node_i.x+node_j.x)/2,(node_i.y+node_j.y)/2,(node_i.z+node_j.z)/2]
        pt2 = [(node_j.x+node_k.x)/2,(node_j.y+node_k.y)/2,(node_j.z+node_k.z)/2]
        self.local_csys = Cartisian(o, pt1, pt2) 
        
        x0=np.array([(node.x,node.y,node.z) for node in self._nodes])
        V=self.local_csys.transform_matrix
        self._x0=(x0-np.array(o)).dot(V.T)[:,:2]
        
        E=self._E
        mu=self._mu
        D0=E/(1-mu**2)
        self._D=np.array([[1,mu,0],
                    [mu,1,0],
                    [0,0,(1-mu)/2]])*D0

        elm_node_count=4
        node_dof=2
        
        Ke = quadpy.quadrilateral.integrate(
            lambda s: self._BtDB(s)*np.linalg.det(self._J(s)),
            quadpy.quadrilateral.rectangle_points([-1.0, 1.0], [-1.0, 1.0]),
            quadpy.quadrilateral.Stroud('C2 7-2')
            )   
        row=[]
        col=[]
        for i in range(elm_node_count):
            row+=[a for a in range(i*node_dof,i*node_dof+node_dof)]
            col+=[a for a in range(i*6,i*6+node_dof)]
        data=[1]*(elm_node_count*node_dof)
        G=sp.sparse.csr_matrix((data,(row,col)),shape=(elm_node_count*node_dof,elm_node_count*6))
        self._Ke=G.transpose()*Ke*G
#        np.set_printoptions(precision=1,suppress=True)
        #Concentrated mass matrix, may be wrong
        self._Me=G.transpose()*np.eye(node_dof*elm_node_count)*G*rho*self._area*t/4
        
        self._re =np.zeros((elm_node_count*6,1))
        
    @property
    def area(self):
        return self._area
        
    def _N(self,x):
        """
        convert csys from x to N
        return: 3x1 array represent x,y
        """
        x,y=x[0],x[1]
        x0,y0=self._x0[:,0],self._x0[:,1]
        N=[]
        for i in range(4):
            N.append((1-x*x0[i])*(1-y*y0[i])/4)
        return np.array(N).reshape(4,1)
    
    def _J(self,x):
        x,y=x[0],x[1]
        x0,y0=self._x0[:,0],self._x0[:,1]
        L=np.array([[-x0[0]*(1-y*y0[0])/4,-y0[0]*(1-x*x0[0])/4],
                    [-x0[1]*(1-y*y0[1])/4,-y0[1]*(1-x*x0[1])/4],
                    [-x0[2]*(1-y*y0[2])/4,-y0[2]*(1-x*x0[2])/4],
                    [-x0[3]*(1-y*y0[3])/4,-y0[3]*(1-x*x0[3])/4],]).T
        R=self._x0
        return np.dot(L,R)
    
    def _B(self,x):
        """
        strain matrix, which is derivative of intepolate function
        """
        B=[]
        x0,y0=self._x0[:,0],self._x0[:,1]
        x,y=x[0],x[1]
        for i in range(4):
            B.append(np.array([[-x0[i]*(1-y*y0[i])/4,                   0],
                               [                   0,-y0[i]*(1-x*x0[i])/4],
                               [-y0[i]*(1-x*x0[i])/4,-x0[i]*(1-y*y0[i])/4]]))
        B=np.hstack(B)
        return B
    
    def _x(self,N):
        """
        convert csys from L to x
        return: 2x1 array represent x,y
        """
        return np.dot(np.array(N).reshape(1,4),self._x0).reshape(2,1)

    def _BtDB(self,x):
        """
        strain matrix, which is derivative of intepolate function
        """
        B=[]
        x0,y0=self._x0[:,0],self._x0[:,1]
        x,y=x[0],x[1]
        for i in range(4):
            B.append(np.array([[-x0[i]*(1-y*y0[i])/4,                 x*0],
                               [                 y*0,-y0[i]*(1-x*x0[i])/4],
                               [-y0[i]*(1-x*x0[i])/4,-x0[i]*(1-y*y0[i])/4]]))
        B=np.hstack(B)
        D=self._D
        BtDB=np.zeros((8,8,B.shape[2]))
        for k in range(B.shape[2]):
            BtDB[:,:,k]=B[:,:,k].transpose().dot(D).dot(B[:,:,k])
        return BtDB
    
    def _S(self,x):
        """
        stress matrix
        """
        return np.dot(self._D,self._B(x))

class Plate4(IsoParametric):
    def __init__(self,node_i, node_j, node_k, node_l,t, E, mu, rho, name=None):
        #8-nodes
        self.__nodes.append(node_i)
        self.__nodes.append(node_j)
        self.__nodes.append(node_k)
        self.__nodes.append(node_l)

        self.__t=t
        
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