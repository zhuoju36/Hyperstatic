# -*- coding: utf-8 -*-
"""
Created on Tue May 19 11:58:29 2020

@author: Dell
"""

import numpy as np
import scipy as sp
from scipy.signal import convolve
from scipy.fftpack import fft,ifft,fftfreq
from matplotlib import pyplot as plt
import os

#设置rc参数显示中文标题
#设置字体为SimHei显示中文
plt.rcParams['font.sans-serif'] = 'SimHei'
#设置正常显示字符
plt.rcParams['axes.unicode_minus'] = False

def read_wave(filename,startline=0):
    a=[]
    flag=False
    with open(filename,"r") as f:
        # a=[]
        # for l in f:
        #     if "'''" in l:
        #         flag=not flag
        #         continue
        #     if flag:
        #         continue
        #     a.append(l.split()[1])
    
    # ag=[float(i) for i in a]
        ag=[float(i) for i in f]
    return list(ag)

def amptitude(wave,a_max):
    m=max(wave)
    return [i*a_max/m for i in wave]

def wave2spectrum(file,dt,ξ,a_max,startline=1):
    """
    file: file
    dt: length of time step
    ξ: damping ratio
    a_max: design peak acceleration
    return:
        T in s, a in g, v in m/s, d in m
    """
    ag=read_wave(os.path.join(file),startline)
    ag=np.array(ag)
    ag=0.01*ag*a_max/np.max(ag)
    # ag=amptitude(ag,a_max)
    # ag=[0.01*i for i in ag]
    T=np.arange(dt,6.0+dt,dt)
    t=np.arange(len(ag))*dt
    β=[]
    sa=[]
    sv=[]
    sd=[]
    for _T in T:
        _ω=2*np.pi/_T
        Sa,Sv,Sd=duhamel(_ω,ξ,t,ag)
        sa.append(max(Sa)/9.8)
        sv.append(max(Sv))
        sd.append(max(Sd))
    return T,sa,sv,sd

def duhamel(ω,ζ,t,p):
    """
    ω: frequency
    ζ: damping
    t: total time
    p: excitation
    """ 
    dt=(t[-1]-t[0])/(len(t)-1)
    ω_=ω*np.sqrt(1-ζ**2)
    q=np.exp(-ζ*ω_*t)*np.sin(ω_*t)
    Sd=1/ω_*convolve(p,q)[:len(t)]*dt
    Sv=Sd*ω_
    Sa=Sv*ω_
    return Sa,Sv,Sd


def fft2spec(file,dt,ξ,a_max):
    """
    file: file
    dt: length of time step
    ξ: damping ratio
    a_max: design peak acceleration, in cm/s2
    return:
        T in s, a in g
    """
    ag=read_wave(os.path.join(file))
    ag=np.array(ag)
    ag=0.01*ag*a_max/np.max(ag) #cm/s2 -> m/s2
    T=np.arange(dt,6.0+dt,dt)
    nex2pow=lambda x: int(round(2**np.ceil(np.log(x)/np.log(2.)))) #求采样点
    im=np.lib.scimath.sqrt(-1)
    Sa=[]
    # for _T in T:
    #     ωₙ=2*np.pi/_T
    #     ωd=(1-ξ)**0.5*ωₙ
    #     n=256#采样点不是太精确，最好取到采样点数
    #     Nfft=nex2pow(n)*16
    #     af=fft(ag,Nfft)/Nfft
    #     f=fftfreq(Nfft,d=dt)
    #     ω=2*np.pi*f
    #     H=1/((1-(ω/ωₙ)**2)+2*ξ*(ω/ωₙ)*im)
    #     u=ifft(af*H,Nfft).real*Nfft
    #     Sa.append(max(u)/9.8)
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



def GB50011_spectrum(αₘₐₓ,Tg,ζ,dt):
    T=np.arange(0,6,dt)
    γ=0.9+(0.05-ζ)/(0.3+6*ζ)
    η1=0.02+(0.05-ζ)/(4+32*ζ)
    η1= η1 if η1>0 else 0
    η2= 1+(0.05-ζ)/(0.08+1.6*ζ)
    η2= η2 if η2>0.55 else 0.55
    def f(t):
        if t<0.1:
            return 0.45*αₘₐₓ+(η2-0.45)*αₘₐₓ/0.1*t
        elif t<Tg:
            return η2*αₘₐₓ
        elif t<5*Tg:
            return (Tg/t)**γ*η2*αₘₐₓ
        else:
            return (η2*0.2**γ-η1*(t-5*Tg))*αₘₐₓ
    return dict([(t,f(t)) for t in T])

def f(t):
    c=0.15
    t1=4
    t2=15
    t3=40
    if t<t1:
        return t**2/t1**2
    elif t<t2:
        return 1
    elif t<t3:
        return np.exp(-c*(t-t2))
    else:
        return 0
    
# def S(wk):
#     def s(wk):
#         Tg=2*pi/wk
#         return GB50011_spectrum(αₘₐₓ,Tg,ζ,T=np.arange(0,6,0.02)):
#     p=0.85
#     return 2*ζ/np/wk*S(wk)**2/(-2*np.ln(-np/wk/Td*np.log(p)))

square_err=lambda x,y: np.sum(np.power((np.array(x)-np.array(y)),2))

if __name__=='__main__':
    import os

    category=os.listdir('D:\\地震波')
    files=os.listdir("D:\\地震波\\"+category[0])
    files=[os.path.join("D:\\地震波",category[0],i) for i in files]

    # amax1={'6':18,''}
    damp=0.05
    num_wave=3
    method='fft'# or 'conv'
    plt.cla()
    avg=[]
    s=GB50011_spectrum(0.08,0.35,damp)
    plt.plot(s['T'],s['alpha'],label='规范谱',color='r')
    MSE=[]
    for file in files:
        dt=0.02
        a_max=35
        if method=='fft':
            T,Sa=fft2spec(file,dt,damp,a_max)
        elif method=='conv':
            T,Sa,Sv,Sd=wave2spectrum(file,dt,damp,a_max)
        avg.append([i for i in Sa]) #cm/s2 -> m/s2
        print(file,'MSE=%4.5f'%square_err(Sa,s['alpha']))
        MSE.append((file,square_err(Sa,s['alpha'])))
    MSE.sort(key=lambda x:x[1])
    champions=MSE[:num_wave]
    [print("*",end='') for i in range(99)]
    print("\nChampions：")
    [print(file,'MSE=%4.5f'%err) for file,err in champions]
    for file,err in champions:
        dt=0.02
        a_max=35
        T,Sa=fft2spec(file,dt,damp,a_max)
        avg.append([i for i in Sa]) #cm/s2 -> m/s2
        name=file.split('\\')[-1]
        if name=='Ofunato_131':
            name='ArtWav'
        plt.plot(T,np.array(Sa),linewidth=0.5,label=name)
    avg=np.array(avg).mean(0)
    plt.plot(T,avg,label='均值',color='b')
    plt.xlabel('周期/s')
    plt.ylabel('影响系数')
    plt.legend()
    plt.show()