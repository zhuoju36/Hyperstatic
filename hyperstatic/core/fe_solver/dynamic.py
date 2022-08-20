# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 10:26:29 2016

@author: HZJ
"""
import os

import logging
import numpy as np
from scipy import linalg
from scipy import sparse as spr
import scipy.sparse.linalg as sl

from hyperstatic.core.fe_model.model import Model
from hyperstatic.core.fe_model.load.loadcase import ModalCase,TimeHistoryCase
from hyperstatic.core.fe_solver import Solver

class ModalSolver(Solver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve(self,casename:str)->bool:
        assembly=super().assembly
        logging.info('solving problem with %d DOFs...'%assembly.DOF)
        setting=assembly.get_loadcase_setting(casename)
        if setting["algorithm"]=='eigen':
            return self.solve_eigen(casename)
        elif setting["algorithm"]=='ritz':
            pass

    def solve_eigen(self,casename:str)->bool:
        assembly=super().assembly
        logging.info('solving problem with %d DOFs...'%assembly.DOF)
        setting=assembly.get_loadcase_setting(casename)
        k=setting['n_modes']
        precase=setting['base_case']
        if precase==None:
            base_case="0"
        
        path=os.path.join(self.workpath,base_case+'.k') #path of the stiff matrix
        if os.path.exists(path):
            K=np.load(path)
        else:
            K=assembly.assemble_K()
            np.save(path,K)
        path=os.path.join(self.workpath,base_case+'.m') #path of the mass matrix
        if os.path.exists(path):
            M=np.load(path)
        else:
            M=assembly.assemble_M()
            np.save(path,M)
    
        K_=assembly.assemble_boundary(casename,K)
        M_=assembly.assemble_boundary(casename,M)

        if k>assembly.DOF:
            logging.info('Warning: the modal number to extract is larger than the system DOFs, only %d modes are available'%assembly.DOF)
            k=assembly.DOF
        omega2s,modes = sl.eigsh(K_,k,M_,sigma=0,which='LM')
        # omega2s,modes =linalg.eig(K_.todense()[6:,6:],M_.todense()[6:,6:])
        mode_= modes.T # row first
        omega2s=omega2s.reshape(k)
        logging.info('Done!')
        path=os.path.join(self.workpath,casename+'.d') #vibration mode, ad nodal displacement
        np.save(path,mode_)
        path=os.path.join(self.workpath,casename+'.o') #omega
        np.save(path,omega2s)
        return True
        
    def solve_ritz(model:Model,n,F):
        pass

class ResponseSpectrumSolver(Solver):

    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve(self,casename:str)->bool:
        assembly=super().assembly

        n=assembly.get_loadcase_setting(casename)['n']
        modal_damp=assembly.get_loadcase_setting(casename)['modal_damp']
        comb=assembly.get_loadcase_setting(casename)['combo']
        modal_case=assembly.get_loadcase_setting(casename)['modal_case']
        spectrum=modal_case=assembly.get_loadcase_setting(casename)['spectrum']

        
        k_path=os.path.join(self.workpath,modal_case+'.k') #path of the stiff matrix
        m_path=os.path.join(self.workpath,modal_case+'.m') #path of the mass matrix
        if not(os.path.exists(k_path) and os.path.exists(m_path)):
            self.solve_eigen(modal_case)
        
        K=np.load(k_path)
        M=np.load(m_path)
        DOF=assembly.DOF

        path=os.path.join(self.workpath,casename+'.d') #vibration mode, ad nodal displacement
        mode=np.load(path)
        path=os.path.join(self.workpath,casename+'.o') #omega
        omega2s=np.load(path)
        omega=np.sqrt(omega2s)
        T=2*np.pi/np.sqrt(omega)

        mode[n:,:]=np.zeros((DOF-n,DOF))#use n modes only.
        mode[:,n:]=np.zeros((DOF,DOF-n))
        M_=np.dot(np.dot(mode.T,M),mode)#generalized mass
        K_=np.dot(np.dot(mode.T,K),mode)#generalized stiffness
        L_=np.dot(np.diag(M),mode)
        px=[]
        Vx=[]
        Xm=[]
        gamma=[]
        mx=np.diag(M)
        for i in range(len(mode)):
            #mass participate factor
            px.append(-np.dot(mode[:,i].T,mx))
            Vx.append(px[-1]**2)
            Xm.append(Vx[-1]/3/m)
            #modal participate factor
            gamma.append(L_[i]/M_[i,i])    
        S=np.zeros((DOF,mode.shape[0]))
        
        for i in range(mode.shape[1]):        
            xi=modal_damp[i]
            y=np.interp(T[i],spectrum[0,:],spectrum[1,:])
            y/=omega2s[i]
            S[:,i]=gamma[i]*y*mode[:,i]

        if comb=='CQC':
            res=0    
            rho=np.diag(np.ones(mode.shape[1]))
            for i in range(mode.shape[1]):
                for j in range(mode.shape[1]):
                    if i!=j:
                        r=T[i]/T[j]
                        rho[i,j]=8*xi**2*(1+r)*r**1.5/((1-r**2)**2+4*xi**2*r*(1+r)**2)
                    res+=rho[i,j]*S[:,i]*S[:,j]
            res=np.sqrt(res)
        elif comb=='SRSS':
            res=0
            for i in range(mode.shape[1]):
                res+=S[:,i]**2
            res=np.sqrt(res)
        path=os.path.join(self.workpath,casename+'.d') #nodal displacement
        np.save(path,res)
        return True

class TimeHistorySolver(Solver):
    def __init__(self,workpath:str,filename:str):
        super().__init__(workpath,filename)

    @property
    def workpath(self):
        return super().workpath

    def solve(self,casename:str):
        assembly=super().assembly
        algo=assembly.get_loadcase_setting(casename)['algorithm']
        if algo=='direct_time_integration':
            self.solve_direct_time_integration(casename)
        elif algo=='modal_decomposition':
            self.solve_modal_decomposition()

    def solve_direct_time_integration(self,casename:str):
        assembly=super().assembly
        logging.info('Solving TIME-HISTORY case {} using DIRECT TIME INTEGRATION'.format(casename))
        setting=assembly.get_loadcase_setting(casename)
        dt=setting["params"]['step_size']
        damping=setting["params"]['damping_ratio']
        
        if setting['base_case']==None:
            base_case="0"
        
        path=os.path.join(self.workpath,base_case+'.k') #stiff matrix
        if os.path.exists(path):
            K=np.load(path)
        else:
            K=assembly.assemble_K()
            np.save(path,K)
        path=os.path.join(self.workpath,base_case+'.m') #mass matrix
        if os.path.exists(path):
            M=np.load(path)
        else:
            M=assembly.assemble_M()
            np.save(path,M)
        
        ########Simple damping

        ########Reileigh Damping
        xi_i=0.05
        xi_j=0.02
        T_i=2.0
        T_j=1.0
        omega_i=2*np.pi/T_i
        omega_j=2*np.pi/T_j
        a0=2*omega_i*omega_j/(omega_j**2-omega_i**2)*(xi_i*omega_j-xi_j*omega_i)
        a1=2*omega_i*omega_j/(omega_j**2-omega_i**2)*(-xi_i/omega_j+xi_j/omega_i)
        C=(a0*M+a1*K).tocoo()
        print(a0,a1)

        #########Cauchy Damping

        K_=assembly.assemble_boundary(casename,K)
        M_=assembly.assemble_boundary(casename,M)
        C_=assembly.assemble_boundary(casename,C)

        u=np.zeros((2,K_.shape[0])) #-dt,0, row-first.
        v=np.zeros((2,K_.shape[0]))
        a=np.zeros((2,K_.shape[0]))
        c0=1/dt/dt
        c1=1/2/dt
        c2=2*c0
        c3=1/c2
        u[0,:]=u[1,:]-dt*v[1,:]+c3*a[1,:] #central diff
        M_hat=c0*M_+c1*C_
#         L,D,perm=linalg.ldl(M_hat)
        tmax,tmin=assembly.get_max_min_step(casename)
        for t in range(tmin):
            f=assembly.assemble_f(casename,t)
            f_=assembly.assemble_boundary(casename,f)
            f_hat=(f_.reshape(1,6)-(K_-c2*M_).dot(u[t,:])-(c0*M_-c1*C_).dot(u[t-1,:])).reshape(6,1)
            d,info=sl.cg(M_hat,f_hat)
            u=np.vstack([u,d])
            # v.append(c1*(-a[t-1]+a[t+1]))
            # a.append(c0*(a[t-1]-2*a[t]+a[t+1]))
        path=os.path.join(self.workpath,casename+'.d')
        np.save(path,u[1:,:]) #neglect t=-1
        return True



    def solve_modal_decomposition(model:Model,n,T,F,u0,v0,a0,xi):
        """
        Solve time-history problems with modal decomposition method.\n
        u0,v0,a0: initial state.\n
        T: time list with uniform interval.\n
        F: list of time-dependent force vectors.\n
        xi: modal damping ratio
        """
        w,f,T,mode=eigen_mode(model,n)
        damp=[]
        w=1/f
        for wn in w:
            damp=[2*xi*w]
        
        d=np.diag()
        dt=T[1]-T[0]
        p=mode.T*f #mode paticipation
        wd=w*np.sqrt(1-xi**2)        
        w_=w*xi
        xi_=xi/np.sqrt(1-xi**2)
        a0=2*xi*w
        a1=wd**2-w**2
        a2=2*w_*wd
        S0=np.exp(-xi*w*dt)*np.sin(wd*dt)
        C0=np.exp(-xi*w*dt)*np.cos(wd*dt)
        S1=-w*S0-wd*C0
        C1=-w*C0-wd*S0
        S2=-a1*S0-a2*C0
        C2=-a1*C0+a2*S0
        B=np.array([
        [S0, C0, 1, dt,dt**2,  dt**3],
        [S1, C1, 0,  1, 2*dt,3*dt**2],
        [S2, C2, 0,  0,    2,   6*dt]
        ])
        C=np.array([
        [-wd, -w,   0,   1,     0,     0],
        [  0,  1,   1,   0,     0,     0],
        [  0,  0,w**2,  a0,     2,     0],
        [  0,  0,   0,w**2,  2*a0,     6],
        [  0,  0,   0,   0,2*w**2,  6*a0],
        [  0,  0,   0,   0,     0,6*w**2]
        ])
        A=B*C
        #construct load vector R
        R=[]
        R0=np.dot(mode.T,F)
        R1=[]
        R2=[]
        R3=[]
        for i in range(len(T)-1):
            R1.append((R0[i+1]-R0[i])/dt)
        R1.append(R1[-1])
        for i in range(len(T)-1):
            R2.append(6/dt**2*(R[i+1]-R[i])+2/dt*(R[i+1]+2*R[i]))
        R2.append(R2[-1])
        for i in range(len(T)-1):
            R3.append((R2[i+1]-R2[i])/dt) 
        R3.append(R3[-1])
        for i in range(len(T)):
            t=T[i]
            R.append(R0[i]+t*R1[i]+t**2/2*R2[i]+t**3/6*R3[i])
        #iterate solve
        y_=[]
        for i in range(len(T)):
            y_.append(A*R_)

    def solve_Newmark_beta(model:Model,T,F,u0,v0,a0,beta=0.25,gamma=0.5):
        """
        beta,gamma: parameters.\n
        u0,v0,a0: initial state.\n
        T: time list with uniform interval.\n
        F: list of time-dependent force vectors.
        """
        dt=T[1]-T[0]
        b1=1/(beta*dt*dt)
        b2=-1/(beta*dt)
        b3=1/2/beta-1
        b4=gamma*dt*b1
        b5=1+gamma*dt*b2
        b6=dt*(1+gamma*b3-gamma)
        K_=self.K+b4*self.C+b1*self.M 
        u=[u0]
        v=[v0]
        a=[a0]
        tt=[0]
        for (t,ft) in zip(T,F):
            ft_=ft+np.dot(self.M,b1*u[-1]-b2*v[-1]-b3*a[-1])+np.dot(self.C,b4*u[-1]-b5*v[-1]-b6*a[-1])
            ut=np.linalg.solve(K_,ft_)
            vt=b4*(ut-u[-1])+b5*v[-1]+b6*a[-1]
            at=b1*(ut-u[-1])+b2*v[-1]+b3*a[-1]
            u.append(ut)
            v.append(vt)
            a.append(at)
            tt.append(t)
        df=pd.DataFrame({'t':tt,'u':u,'v':v,'a':a})
        return df
        
    def solve_Wilson_theta(model:Model,T,F,u0=0,v0=0,a0=0,beta=0.25,gamma=0.5,theta=1.4):
        """
        beta,gamma,theta: parameters.\n
        u0,v0,a0: initial state.\n
        T: time list with uniform interval.\n
        F: list of time-dependent force vectors.
        """
        dt=T[1]-T[0]
        dt_=theta*dt
        b1=1/(beta*dt_**2)
        b2=-1/(beta*dt_)
        b3=(1/2-beta)/beta
        b4=gamma*dt_*b1
        b5=1+gamma*dt_*b2
        b6=dt_*(1+gamma*b3-gamma)
        K_=self.K+b4*self.C+b1*self.M 
        u=[u0]
        v=[v0]
        a=[a0]
        tt=[0]

        R_=[F[0]]
        for i in range(len(F)-1):
            R_.append(F[i]+theta*(F[i+1]-F[i]))
            
        for (t,ft) in zip(T,R_):
            ft_=ft+np.dot(self.M,b1*u[-1]-b2*v[-1]-b3*a[-1])+np.dot(self.C,b4*u[-1]-b5*v[-1]-b6*a[-1])
            ut_=np.linalg.solve(K_,ft_)
            vt_=b4*(ut_-u[-1])+b5*v[-1]+b6*a[-1]
            at_=b1*(ut_-u[-1])+b2*v[-1]+b3*a[-1]          
            
            at=a[-1]+1/theta*(at_-a[-1])
            vt=v[-1]+((1-gamma)*a[-1]+gamma*at)*dt
            ut=u[-1]+v[-1]*dt+(1/2-beta)*a[-1]*dt**2+beta*at*dt**2

            u.append(ut)
            v.append(vt)
            a.append(at)
            tt.append(t)
        df=pd.DataFrame({'t':tt,'u':u,'v':v,'a':a})
        return df

if __name__=='__main__':
    spr.diags()
    import sys
    from hyperstatic.core.fe_model.assembly import Assembly
    from hyperstatic.core.fe_model.model import Model
    from hyperstatic.core.fe_model.load.pattern import LoadPattern
    from hyperstatic.core.fe_model.load.loadcase import ModalCase
    from hyperstatic.common.curve import Curve

    path="./test"
    if sys.platform=="win32":
        path="c:\\test"

    model=Model()
    model.add_node("1",0,0,0)
    model.add_node("2",6,0,0)
    model.add_isotropic_material('steel',7849.0474,2e11,0.3,1.17e-5)
    model.add_beam_section_I('H400x200x20x30','steel',0.4,0.2,0.02,0.03)
    model.add_beam("A","1","2",'H400x200x20x30')
    model.set_nodal_restraint("1",True,True,True,True,True,True)
    # model.set_nodal_mass("2",1,1,1,1,1,1)

    lc1=ModalCase("eigen",3)
    lc1.use_load_as_mass=False

    curve=Curve.sin('sine',A=10,w=1,phi=1,dt=0.1,n=100).to_array()

    lc2=TimeHistoryCase("time_history",curve)
    lc2.use_direct_time_integration(step_size=0.1)

    asb=Assembly(model,[lc1,lc2])
    asb.save(path,"test.asb")

    solver=ModalSolver(path,"test.asb")
    solver.solve("eigen")
    omega2=np.load(os.path.join(path,"eigen.o.npy"))
    d=np.load(os.path.join(path,"eigen.d.npy"))
    print(2*np.pi/np.sqrt(omega2))
    print(d.T)

    solver=TimeHistorySolver(path,"test.asb")
    solver.solve("time_history")
    d=np.load(os.path.join(path,"time_history.d.npy"))
