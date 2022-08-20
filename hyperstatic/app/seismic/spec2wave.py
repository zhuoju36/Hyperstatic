import numpy as np
import scipy as sp
from scipy.signal import convolve
from scipy.fftpack import fft,ifft,fftfreq
from matplotlib import pyplot as plt
import os
from wave2spec import GB50011_spectrum
from random import random

dω=0.02*2*np.pi#Hz 频率间隔
ωk=np.arange(2*np.pi/6,2*np.pi/0.02,dω) #第k个谐波分量的圆频率，共n个 max(ωk)<1
Ψk=np.random.random(len(ωk))*np.pi*2

dt=0.01#s 时间间隔
t=np.arange(0.1,40,dt) #时间点

r=0.15 #超越概率
ζ=0.05 #阻尼比
td=20#s 持续时间

PGA=70 #cm/s^2

S=GB50011_spectrum(PGA/440,0.45,ζ,dt) #目标谱

def f(t):
    t1=10
    t2=20
    c=0.1
    if 0<t<=t1:
        return (t/t1)**2
    elif t1<t<t2:
        return 1
    else:
        return np.exp(-c*(t-t2))

def ST(ω):
    xp=2*np.pi/np.array(list(S.keys()))
    fp=list(S.values())
    return np.interp(ω,xp,fp)

Sτ=lambda ωk: ζ/(np.pi*ωk)*(ST(ωk)**2)/(np.log(-np.pi*np.log((1-r)/(ωk*td))))

def Sτ_(ωk):
    s=Sτ(ωk) #功率谱
    st=ST(ωk) #目标反应谱
    sa=Sa(ωk) #时程反应谱
    for i in range(10):
        s*=st/sa
    return s

Ck=lambda ωk: np.sqrt(4*Sτ(ωk)*dω)

alpha = lambda t: Ck(ωk).dot(np.cos(ωk*t+Ψk))

A = lambda t: f(t)*alpha(t)

A=np.vectorize(A)

import matplotlib.pyplot as plt

plt.plot(t,A(t))

def fft2spec(ag,dt,ξ,a_max):
    """
    dt: length of time step
    ξ: damping ratio
    a_max: design peak acceleration, in cm/s2
    return:
        T in s, a in g
    """
    ag=0.01*ag*a_max/np.max(ag) #cm/s2 -> m/s2
    T=np.arange(dt,6.0+dt,dt)
    nex2pow=lambda x: int(round(2**np.ceil(np.log(x)/np.log(2.)))) #求采样点
    im=np.lib.scimath.sqrt(-1)
    Sa=[]
    n=256#采样点不是太精确，最好取到采样点数
    Nfft=nex2pow(n)*16
    f=fftfreq(Nfft,d=dt)
    ω=2*np.pi*f
    def max_response(_T):
        ωₙ=2*np.pi/_T
        ωd=(1-ξ)**0.5*ωₙ
        af=fft(ag,Nfft)/Nfft    
        # H=1/((1-(ω/ωₙ)**2)+2*ξ*(ω/ωₙ)*im) #ωd?
        H=1/((1-(ω/ωd)**2)+2*ξ*(ω/ωd)*im)
        u=ifft(af*H,Nfft).real*Nfft
        return np.max(u)/9.8
    Sa=[max_response(t) for t in T]
    return T,Sa


T,Sa=fft2spec(A(t),dt,ζ,PGA)
plt.plot(T,Sa)

def A_fit(t):
    s=Sτ(ωk) #功率谱
    st=ST(ωk) #目标反应谱
    for i in range(10): 
        Ck=np.sqrt(4*s*dω)
        alpha = lambda t: Ck.dot(np.cos(ωk*t+Ψk))
        A = np.vectorize(lambda t: f(t)*alpha(t) )
        accel=A(t)
        T,Sa_=fft2spec(accel,dt,ζ,PGA)
        def Sa(ωk):
            xp=2*np.pi/np.array(T)
            fp=np.array(Sa_)
            return np.interp(ωk,xp,fp)
        sa=Sa(ωk) #时程反应谱
        s*=(st/sa)
    return A(t)

accel=A_fit(t)
PGA=70
T,Sa=fft2spec(accel,dt,ζ,PGA)
plt.plot(T,Sa)
plt.plot(list(S.keys()),list(S.values()))
    