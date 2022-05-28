# -*- coding: utf-8 -*-
import numpy as np

class LoadPattern(object):
    def __init__(self,name:str):
        self.__name=name
        self.__nodal_load={}
        self.__nodal_disp={}
        self.__beam_distributed={}
        self.__beam_concentrated={}

    @property
    def name(self):
        return self.__name

    def set_nodal_load(self,name,f1=0,f2=0,f3=0,m1=0,m2=0,m3=0):
        self.__nodal_load[name]=np.array([f1,f2,f3,m1,m2,m3])

    def set_nodal_disp(self,name,u1=0,u2=0,u3=0,r1=0,r2=0,r3=0):
        self.__nodal_disp[name]=np.array([u1,u2,u3,r1,r2,r3])

    def set_beam_load_dist(self,name,pi=0,pj=0,qi2=0,qj2=0,qi3=0,qj3=0,ti=0,tj=0):
        self.__beam_distributed[name]=np.array([pi,qi2,qi3,ti,0,0,pj,qj2,qj3,tj,0,0])

    def set_beam_load_conc(self,name,F1=0,F2=0,F3=0,M1=0,M2=0,M3=0,r=0.5):
        self.__beam_concentrated[name]=np.array([F1,F2,F3,M1,M2,M3,r]) 

    def get_nodal_f(self,name):
        if name in self.__nodal_load.keys():
            return self.__nodal_load[name]
        else:
            return None

    def get_nodal_f_dict(self):
        return self.__nodal_load.copy()

    def get_nodal_d(self,name):
        if name in self.__nodal_disp.keys():
            return self.__nodal_disp[name]
        else:
            return None

    def get_nodal_d_dict(self):
        return self.__nodal_disp.copy()

    def get_beam_distributed(self,name):
        if name in self.__beam_distributed.keys():
            return self.__beam_distributed[name]
        return None

    def get_beam_concentrated(self,name):
        if name in self.__beam_distributed.keys():
            return self.__beam_distributed[name]
        return None

    def get_beam_f(self,name,l):
        r=np.zeros(12)
        if name in self.__beam_distributed.keys():
            v=self.__beam_distributed[name]

            q1=v[6] #axial
            q2=v[0]-v[6]
            r[0]+= q1*l/2+0.5*q2*l*(2/3)
            r[6]+= q1*l/2+0.5*q2*l*(1/3)

            q1=v[7] #axis 2
            q2=v[1]-v[7]
            r[1]+=q1*l/2+7/20*q2*l #shear i
            r[5]+=q1*l*l/12+q2*l*l/20 #bending i
            r[7]+=q1*l/2+3/20*q2*l #shear j
            r[11]+=-q1*l*l/12-q2*l*l/30 #bending j
            # w1,w2=v[1],v[7]
            # l1=l2=0
            # r[1]+=w1*(l-l1)**3/20/l**3*((7*l+8*l1)-l2*(3*l+2*l1)/(l-l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)+2*l2**4/(l-l1)**3)+\
            #     w2*(l-l1)**3/20/l**3*((3*l+2*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)-l2**3/(l-l1)**2*(2+(15*l-8*l2)/(l-l1)))
            # r[5]+=(w1+w2)/2*(l-l1-l2)-r[1]
            # r[7]+=w1*(l-l1)**3/60/l**2*(3*(l+4*l1)-l*(2*l+3*l1)/(l-l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)+3*l2**4/(l-l1)**3)+\
            #     w2*(l-l1)**3/60/l**2*((2*l+3*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2))+\
            #     w2*(l-l1)**3/60/l**2*((2*l+3*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)-3*l2**3/(l-l1)**2*(1+(5*l-4*l2)/(l-l1)))
            # r[11]+=(l-l1-l2)/6*(w1-(2*l+2*l1-l2)-w2*(l-l1+2*l2))+r[1]*l-r[7]


            q1=v[8]
            q2=v[2]-v[8]
            r[2]+=q1*l/2+7/20*q2*l #shear i
            r[4]-=q1*l*l/12+q2*l*l/20 #bending i
            r[8]+=q1*l/2+3/20*q2*l #shear j
            r[10]-=-q1*l*l/12-q2*l*l/30 #bending j
            # w1,w2=v[2],v[8]
            # l1=l2=0
            # r[2]+=w1*(l-l1)**3/20/l**3*((7*l+8*l1)-l2*(3*l+2*l1)/(l-l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)+2*l2**4/(l-l1)**3)+\
            #     w2*(l-l1)**3/20/l**3*((3*l+2*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)-l2**3/(l-l1)**2*(2+(15*l-8*l2)/(l-l1)))
            # r[4]+=(w1+w2)/2*(l-l1-l2)-r[1]
            # r[8]+=w1*(l-l1)**3/60/l**2*(3*(l+4*l1)-l*(2*l+3*l1)/(l-l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)+3*l2**4/(l-l1)**3)+\
            #     w2*(l-l1)**3/60/l**2*((2*l+3*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2))+\
            #     w2*(l-l1)**3/60/l**2*((2*l+3*l1)*(1+l2/(l-l1)+l2**2/(l-l1)**2)-3*l2**3/(l-l1)**2*(1+(5*l-4*l2)/(l-l1)))
            # r[10]+=(l-l1-l2)/6*(w1-(2*l+2*l1-l2)-w2*(l-l1+2*l2))+r[2]*l-r[8]

            q1=v[9] #torsion
            q2=v[3]-v[9]
            r[3]+= q1*l/2+0.5*q2*l/3
            r[9]+= -q1*l/2-0.5*q2*l/6
            # w=v[3]
            # r[3]+= w/2/l*(l-l1-l2)*(l-l1+l2)
            # r[9]+= w/2/l*(l-l1-l2)*(l+l1-l2)

            # q1=v[4] #bending 2
            # q2=v[4]-v[10]
            # r[1]+=-q1*6/4+(q2/2)*(1/3)*(2/3)*6 #shear i
            # r[7]+=q1*6/4-(q2/2)*(1/3)*(2/3)*6 #shear j
            # r[5]+= -q1*l/4 - q2*l*(-(1*l/3)*(3*(2/3)-l)/l)
            # r[11]+= -q1*l/4 - q2*l*(-(2*l/3)*(3*(1*l/3)-l)/l)

            # q1=v[5] #bending 3
            # q2=v[5]-v[11]
            # r[2]+=-q1*6/4+(q2/2)*(1/3)*(2/3)*6 #shear i
            # r[8]+=q1*6/4-(q2/2)*(1/3)*(2/3)*6 #shear j
            # r[4]+= -q1*l/4 - q2*l*(-(2*l/3)*(3*(l/3)-l)/l)
            # r[10]+= -q1*l/4 - q2*l*(-(l/3)*(3*(2*l/3)-l)/l)

        if name in self.__beam_concentrated.keys():
            v=self.__beam_concentrated[name]
            #TODO correct this
            ra=v[6]
            a=l*ra
            b=l*(1-ra)
            #TODO test it
            r[0]+=v[0]*a*b*b/l/l

            r[1]+=v[1]*b**2*(l+2*a)/(l**3) + v[5]*(-6*a*b/l**3)
            r[2]+=v[2]*b**2*(l+2*a)/(l**3) + v[4]*(-6*a*b/l**3)

            r[3]+=v[3]*b/l
            r[4]+=v[1]*(-a*b*b/l/l)+v[4]*(-b*(3*a-l)/l)
            r[5]+=v[2]*(-a*b*b/l/l)+v[5]*(-b*(3*a-l)/l)

            r[6]+=(-v[0]*a*a*b/l/l)

            r[7]+=v[1]*a**2*(l+2*b)/(l**3) + v[5]*(-6*a*b/l**3)
            r[8]+=v[2]*a**2*(l+2*b)/(l**3) + v[4]*(-6*a*b/l**3)

            r[9]+=v[3]*a/l

            r[10]+=v[1]*a*a*b/l/l+v[4]*(-a*(3*b-l)/l)
            r[11]+=v[2]*a*a*b/l/l+v[5]*(-a*(3*b-l)/l)
        return r

    def get_beam_f_dict(self,ldict):
        r={}
        for k,v in self.__beam_distributed.items():
            l=ldict[k]
            if k not in r.keys():
                r[k]=np.zeros(12)
            r[k][0]+=(v[0]+v[6])*l/2 #axial
            r[k][6]+=(v[0]+v[6])*l/2
            r[k][3]+=(v[0]+v[6])*l/2 #torsion
            r[k][9]+=(v[0]+v[6])*l/2

            q1=v[1] #axis 2
            q2=v[1]-v[7]
            r[k][1]+=q1*l/2+7/20*q2*l #shear i
            r[k][5]+=-q1*l*l/12-q2*l*l/20 #bending i
            r[k][7]+=-q1*l/2-3/20*q2*l #shear j
            r[k][11]+=q1*l*l/12+q2*l*l/30 #bending j
            q1=v[2]
            q2=v[2]-v[8]
            r[k][2]+=q1*l/2+7/20*q2*l #shear i
            r[k][6]+=-q1*l*l/12-q2*l*l/20 #bending i
            r[k][8]+=-q1*l/2-3/20*q2*l #shear j
            r[k][10]+=q1*l*l/12+q2*l*l/30 #bending j

        for k,v in self.__beam_concentrated.items():
            l=ldict[k]
            if k not in d.keys():
                r[k]=np.zeros(12)
            #TODO correct this
            ra=v[6]
            a=l*ra
            b=l*(1-ra)
            #TODO test it
            r[k][0]+=v[0]*a*b*b/l/l

            r[k][1]+=v[1]*b**2*(l+2*a)/(l**3) + v[5]*(-6*a*b/l**3)
            r[k][2]+=v[2]*b**2*(l+2*a)/(l**3) + v[4]*(-6*a*b/l**3)

            r[k][3]+=v[3]*b*(3*a-l)/l
            r[k][4]+=v[1]*(-a*b*b/l/l)+v[4]*(-b*(3*a-l)/l)
            r[k][5]+=v[2]*(-a*b*b/l/l)+v[5]*(-b*(3*a-l)/l)

            r[k][6]+=(-v[0]*a*a*b/l/l)

            r[k][7]+=v[1]*a**2*(l+2*b)/(l**3) + v[5]*(-6*a*b/l**3)
            r[k][8]+=v[2]*a**2*(l+2*b)/(l**3) + v[4]*(-6*a*b/l**3)

            r[k][9]+=v[3]*a*(3*b-l)/l

            r[k][10]+=v[1]*a*a*b/l/l+v[4]*(-a*(3*b-l)/l)
            r[k][11]+=v[2]*a*a*b/l/l+v[5]*(-a*(3*b-l)/l)
        return r

    # def set_node_force(self,node,force,append=False):
    #     """
    #     add node force to model.
    #     params:
    #         node: int, hid of node
    #         force: list of 6 of nodal force
    #         append: bool, if True, the input force will be additional on current force.
    #     return:
    #         bool, status of success
    #     """
    #     assert(len(force)==6)
    #     if append:
    #         self.__nodes[node].fn+=np.array(force).reshape((6,1))
    #     else:
    #         self.__nodes[node].fn=np.array(force).reshape((6,1))
    
    # def set_node_displacement(self,node,disp,append=False):
    #     """
    #     add node displacement to model
        
    #     params:
    #         node: int, hid of node
    #         disp: list of 6 of nodal displacement
    #         append: bool, if True, the input displacement will be additional on current displacement.
    #     return:
    #         bool, status of success
    #     """
    #     assert(len(disp)==6)
    #     if append:
    #         self.__nodes[node].dn+=np.array(disp).reshape((6,1))
    #     else:
    #         self.__nodes[node].dn=np.array(disp).reshape((6,1))
        
if __name__=="__main__":
    import numpy as np

    load=LoadPattern("test")
        #fi,qi2,qi3, ti,mi2,mi3; fj,qj2,qj3, tj,mj2,mj3;
    inp=np.array([
        [1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0],
        [0,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0],
        ])
    oup=np.array([
        [-1/2, 0,  0,  0,  0,  0,  0, -1/2,  0,  0,  0,  0],
        [0, 0.5, 0, 0, 0, -1/12, 0, -0.5, 0, 0, 0, 1/12],
        ])
    for i,o in zip(inp,oup):
        load.set_beam_load_dist("1",*tuple(i))
        fd=load.get_beam_f("1",1)
        assert np.allclose(fd,o) == True
