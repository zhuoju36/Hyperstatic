# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 14:02:33 2017

@author: Dell
"""
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib import pyplot as plt

class code_spectrum(object):
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
    cs1=code_spectrum(0.12,0.45,0.02)
    cs2=code_spectrum(0.34,0.45,0.02)
    cs3=code_spectrum(0.72,0.45,0.02)
    
    font = FontProperties(fname=r"C:\\WINDOWS\\Fonts\\simsun.ttc", size=14)#C:\WINDOWS\Fonts
    plt.xlabel('T(s)',fontproperties=font)
    plt.ylabel('α',fontproperties=font)
    plt.plot(cs1.spectrum['T'],cs1.spectrum['alpha'],label=u'小震')
    plt.plot(cs2.spectrum['T'],cs2.spectrum['alpha'],label=u'中震')
    plt.plot(cs3.spectrum['T'],cs3.spectrum['alpha'],label=u'大震')
    plt.legend(prop=font)