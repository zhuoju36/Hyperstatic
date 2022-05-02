# -*- coding: utf-8 -*-

from time import ctime
import threading

def info(log:str,target='console'):
    """
    log: text to record.
    target: 'console' to print log on screen or file to write in. 
    """
    if target=='console':
        thd=threading.Thread(target=print,args=(ctime(),':',log))
        thd.setDaemon(True)
        thd.start()
        thd.join()
    else:
        try:
            thd=threading.Thread(target=print,args=(ctime(),':',log))
            thd.setDaemon(True)
            thd.start()
            thd.join()
        except Exception as e:
            print(e)
                
def write_file(text,target):
    try:
        f=open(target)
        f.write(text)      
    except Exception as e:
        print(e)
    finally:
        f.close()