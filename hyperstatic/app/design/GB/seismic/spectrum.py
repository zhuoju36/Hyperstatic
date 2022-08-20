# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 14:02:33 2017

@author: Dell
"""
import numpy as np
#from matplotlib.font_manager import FontProperties
from matplotlib import pyplot as plt

class GB50010(object):
    def __init__(self,alpha_max,Tg,xi):
        gamma=0.9+(0.05-xi)/(0.3+6*xi)
        eta1=0.02+(0.05-xi)/(4+32*xi)
        eta1=eta1 if eta1>0 else 0
        eta2=1+(0.05-xi)/(0.08+1.6*xi)
        eta2=eta2 if eta2>0.55 else 0.55
        T=np.linspace(0,6,601)
        alpha=[]
        for t in T:
            if t<0.1:
                alpha.append(np.interp(t,[0,0.1],[0.45*alpha_max,eta2*alpha_max]))
            elif t<Tg:
                alpha.append(eta2*alpha_max)
            elif t<5*Tg:
                alpha.append((Tg/t)**gamma*eta2*alpha_max)
            else:
                alpha.append((eta2*0.2**gamma-eta1*(t-5*Tg))*alpha_max)
        self.__spectrum={'T':T,'alpha':alpha}
     
    @property
    def spectrum(self):
        return self.__spectrum
        
if __name__=='__main__':
    Tg=0.90
    xi=0.02
    cs1=GB50010(0.12,Tg,xi)
    cs2=GB50010(0.34,Tg,xi)
    cs3=GB50010(0.72,Tg,xi)
    
#    font = FontProperties(fname=r"C:\\WINDOWS\\Fonts\\simsun.ttc", size=14)#C:\WINDOWS\Fonts
#    plt.xlabel('T(s)',fontproperties=font)
#    plt.ylabel('α',fontproperties=font)
    plt.plot(cs1.spectrum['T'],cs1.spectrum['alpha'],label=u'小震')
    plt.plot(cs2.spectrum['T'],cs2.spectrum['alpha'],label=u'中震')
    plt.plot(cs3.spectrum['T'],cs3.spectrum['alpha'],label=u'大震')
#    plt.legend(prop=font)
    
    cs=cs1
    for (t,a) in zip(cs.spectrum['T'],cs.spectrum['alpha']):
        if np.mod(t*100,10)==0:
            print(t,a)

def wind_vibration_factor():         
    g=2.5
    I10=0.12
    xi1=0.01
    k_w=1.28
    f1=1/1.38
    w0=0.65
    k=0.944
    a1=0.155
    H=30
    B=max(100,2*H)
    rho_z=10*np.sqrt(H+60*np.e**(-H/60)-60)/H
    rho_x=10*np.sqrt(H+50*np.e**(-H/60)-50)/B
    mu_z=1.67
    phi1=1
    Bz=k*H**a1*rho_x*rho_z*phi1/mu_z
    x1=min([30*f1/np.sqrt(k_w*w0),5])
    R=np.sqrt(np.pi*x1**2/(6*xi1*(1+x1**2)**(4/3)))
    beta_z=1+2*g*I10*Bz*np.sqrt(1+R**2)
    print(beta_z)

#
#mass=2.22831e3*0.011*7850+641172+276159.5-12370.6
#print(mass)
##mass=(2.22831e3*0.021+3.4817e3*0.025+1.05e3*0.14+0.739e3*0.012)*7850+37202
#area=3.481e3
#print(mass/1000)
#print(mass/area)
##
#def comfortablity():
#    C=2
#    B=95.7
#    L=43.5
#    w_=12+0.3
#    p0=0.3
#    g=9.8
#    beta=0.02
#    w=w_*C*L*L
#    fn=2.47
#    Fp=p0*np.exp(-0.35*fn)
#    a_p=Fp/(beta*w)*g
##    print(w)
##    print(Fp)
##    print(a_p)
#
#weight=(3.482e3*0.020+2.631e3*0.012+649*0.008+1.25e3*0.012)*7.85
#print('weight(t)')
#print(weight)
#
#w1=274*1.2
#w2=(196+1000)*1.2
#print(w1)