# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 10:26:29 2016

@author: HZJ
"""

import numpy as np
from scipy import linalg
from scipy import sparse as sp
import scipy.sparse.linalg as sl

from structengpy.fe_model.model import Model
import logger
from structengpy.fe_solver import Solver 

class StaticSolver(Solver):
    def __init__(self,workpath:str):
        super.__init__(workpath)

    def solve_modal(self,k:int):
        """
        Solve eigen mode of the MDOF system
        
        params:
            model: FEModel.
            k: number of modes to extract.
        """
        model=self.model
        K_,M_=model.K_,model.M_
        if k>model.DOF:
            logger.info('Warning: the modal number to extract is larger than the system DOFs, only %d modes are available'%model.DOF)
            k=model.DOF
        omega2s,modes = sl.eigsh(K_,k,M_,sigma=0,which='LM')
        delta = modes/np.sum(modes,axis=0)
        model.is_solved=True
        model.mode_=delta
        model.omega_=np.sqrt(omega2s).reshape((k,1))
        
    def Riz_mode(model:Model,n,F):
        """
        Solve the Riz mode of the MDOF system\n
        n: number of modes to extract\n
        F: spacial load pattern
        """
        #            alpha=np.array(mode).T
    #            #Grum-Schmidt procedure            
    #            beta=[]
    #            for i in range(len(mode)):
    #                beta_i=alpha[i]
    #                for j in range(i):
    #                    beta_i-=np.dot(alpha[i],beta[j])/np.dot(alpha[j],alpha[j])*beta[j]
    #                beta.append(beta_i)
    #            mode_=np.array(beta).T
        pass

    def spectrum_analysis(model,n,spec):
        """
        sepctrum analysis
        
        params:
            n: number of modes to use\n
            spec: a list of tuples (period,acceleration response)
        """
        freq,mode=eigen_mode(model,n)
        M_=np.dot(mode.T,model.M)
        M_=np.dot(M_,mode)
        K_=np.dot(mode.T,model.K)
        K_=np.dot(K_,mode)
        C_=np.dot(mode.T,model.C)
        C_=np.dot(C_,mode)
        d_=[]
        for (m_,k_,c_) in zip(M_.diag(),K_.diag(),C_.diag()):
            sdof=SDOFSystem(m_,k_)
            T=sdof.omega_d()
            d_.append(np.interp(T,spec[0],spec[1]*m_))
        d=np.dot(d_,mode)
        #CQC
        return d
        
    def modal_decomposition(model:Model,n,T,F,u0,v0,a0,xi):
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

    def response_spectrum(model:Model,spec,mdd,n=60,comb='CQC'):
        """
        spec: a {'T':period,'a':acceleration} dictionary of spectrum\n
        mdd: a list of modal damping ratio\n
        comb: combination method, 'CQC' or 'SRSS'
        """
        K=model.K_
        M=model.M_
        DOF=model.DOF
        w,f,T,mode=eigen_mode(model,DOF)
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
            xi=mdd[i]
            y=np.interp(T[i],spec['T'],spec['a'])
            y/=w[i]**2
            S[:,i]=gamma[i]*y*mode[:,i]

        if comb=='CQC':
            cqc=0    
            rho=np.diag(np.ones(mode.shape[1]))
            for i in range(mode.shape[1]):
                for j in range(mode.shape[1]):
                    if i!=j:
                        r=T[i]/T[j]
                        rho[i,j]=8*xi**2*(1+r)*r**1.5/((1-r**2)**2+4*xi**2*r*(1+r)**2)
                    cqc+=rho[i,j]*S[:,i]*S[:,j]
            cqc=np.sqrt(cqc)
            print(cqc)
        elif comb=='SRSS':
            srss=0
            for i in range(mode.shape[1]):
                srss+=S[:,i]**2
            srss=np.sqrt(srss)
            print(srss)
        
        
    def Newmark_beta(model:Model,T,F,u0,v0,a0,beta=0.25,gamma=0.5):
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
        
    def Wilson_theta(model:Model,T,F,u0=0,v0=0,a0=0,beta=0.25,gamma=0.5,theta=1.4):
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