from wave2spec import *

square_err=lambda x,y: np.sum(np.power((np.array(x)-np.array(y)),2))

import os
import time

def select(files,amax,Tg,damp,sensitive=(0,6),num_wave=5):
    Tdomain=sensitive
    method='fft'# or 'conv'
    plt.cla()
    avg=[]
    dt=0.01
    s=GB50011_spectrum(amax,Tg,damp,dt)
    plt.plot(list(s.keys()),list(s.values()),label='规范谱',color='r')
    MSE=[]
    for file in files:
        new_dt=file.split(' ')[-1]
        new_dt=float(new_dt[:-4])
        if new_dt!=dt:
            dt=new_dt
            s=GB50011_spectrum(amax,Tg,damp,dt)
        peak=amax*440 #peak acceleration, 
        # beg=time.time()
        if method=='fft':
            T,Sa=fft2spec(file,dt,damp,peak)
        elif method=='conv':
            T,Sa,Sv,Sd=wave2spectrum(file,dt,damp,peak)
        # print("T=",time.time()-beg)
        domain=[i for i,t in zip(range(len(s)),s.keys()) if Tdomain[0]<=t<=Tdomain[1]]
        SE=square_err(Sa[domain[0]:domain[-1]],
            list(s.values())[domain[0]:domain[-1]]
            )
        print(file,'MSE=%4.5f'%SE)
        MSE.append((file,SE)) #only consider MSE in sensitive domain
    MSE.sort(key=lambda x:x[1])
    champions=MSE[:num_wave]
    [print("*",end='') for i in range(99)]
    print("\nChampions：")
    [print(file,'MSE=%4.5f'%err) for file,err in champions]
    Tp=np.arange(0,6,0.01)
    for file,err in champions:
        T,Sa=fft2spec(file,dt,damp,peak)
        interpSa=np.interp(Tp,T,Sa)
        avg.append(interpSa)
        name=file.split('\\')[-1]
        plt.plot(T,np.array(Sa),linewidth=0.5,label=name)
    
    avg=np.array(avg).mean(0)
    plt.plot(Tp,avg,label='均值',color='b')
    plt.xlabel('周期/s')
    plt.ylabel('影响系数')
    plt.legend()
    plt.show()

if __name__=='__main__':
    Tg=0.55
    root=os.path.join('wave_lib','Tg=%3.2fs'%Tg)
    files=[os.path.join(root,i) for i in os.listdir(root)]
    files=[i for i in files if os.path.isfile(i)]
    select(files,amax=0.16,Tg=Tg,damp=0.02,sensitive=(0.5,1.4),num_wave=7)