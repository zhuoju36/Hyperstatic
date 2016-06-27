# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 16:26:46 2016

@author: huan
"""
import sqlite3

class DataManager:
    def __init__(self,db):
        self.db=db
        
    def __del__(self):
        self.Close()
        
    def Connect(self):
        try:
            self.conn = sqlite3.connect(self.db)
        except:
            print('error')
    def Close(self):
        self.conn.close()
        

    