# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 16:26:46 2016

@author: huan
"""
import sqlite3

class DataManager:
    def Connect(self,db):
        try:
            self.conn = sqlite3.connect(db)
        except:
            print('error')
    def Close(self):
        self.conn.close()