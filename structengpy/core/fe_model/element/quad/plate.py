import numpy as np
import scipy as sp
import scipy.sparse as spr

from structengpy.core.fe_model.element.quad import Quad

class Plate4(Quad):
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

    def _N(self,s,r):
        """
        params:
            Hermite's interpolate function
            s:natural position of evalue point.
        returns:
            3x(3x16) shape function matrix.
        """
        H11=1-3*s**2+2*s**3
        H12=  3*s**2-2*s**3
        H21=s-2*s**2+s**3
        H22=   -s**2+s**3
        H31=1-3*r**2+2*r**3
        H32=  3*r**2-2*r**3
        H41=r-2*r**2+r**3
        H42=   -r**2+r**3
        N1=H11*H31
        N2=H11*H41
        N3=H12*H31
        N4=H12*H41
        N5=H11*H32
        N6=H11*H42
        N7=H12*H32
        N8=H12*H42
        N9=H21*H31
        N10=H21*H41
        N11=H22*H31
        N12=H22*H41
        N13=H21*H32
        N14=H21*H42
        N15=H22*H32
        N16=H22*H42
        N=np.hstack([np.eye(3)*N1,np.eye(3)*N2,np.eye(3)*N3,np.eye(3)*N4,
                     np.eye(3)*N5,np.eye(3)*N6,np.eye(3)*N7,np.eye(3)*N8,
                     np.eye(3)*N9,np.eye(3)*N10,np.eye(3)*N11,np.eye(3)*N12,
                     np.eye(3)*N13,np.eye(3)*N14,np.eye(3)*N15,np.eye(3)*N16])
        return N

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
