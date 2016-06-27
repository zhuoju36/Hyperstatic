# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 16:32:51 2016

@author: huan
"""

import sys
import sqlite3
sys.path.append('..')
from DataManager import DataManager
import pandas as pd

class Materials(DataManager):
    def __init__(self,db):
        DataManager.__init__(self,db)
    
    def CreateTable(self):
        cu=self.conn.cursor()
        sql=[]
        sql.append(
        'CREATE TABLE Material_Properties_General (\
        Name TEXT UNIQUE PRIMARY KEY, \
        Type TEXT, \
        SymType TEXT, \
        TempDepend TEXT, \
        Color REAL)'
        )
        cu.execute(sql)
        
    def AddCartesian(self,nodes):
        cu=self.conn.cursor()
        for node in nodes:
            val=(str(node.name),str(node.name),'Global','Cartesian',str(node.x),str(node.y),str(node.z))
            cu.execute('INSERT INTO Node_Coordinates VALUES (?,?,?,?,?,?,?)',val)
        self.conn.commit()
                
    def Count():
        return False
        
    def GetCoordCartesian():
        return False
        
class Node:
    def __init__(self,guid,name,c1,c2,x,y,z):
        self.guid,self.name,self.c1,self.c2,self.x,self.y,self.z=guid,name,c1,c2,x,y,z

if __name__=='__main__':
    df=pd.read_csv('d:\\testnode.csv',header=None)
    nodes=[]
    for i in range(df.shape[0]):
        node=df.ix[i]
        nodes.append(Node(node[0],node[0],node[1],node[2],node[3],node[4],node[5]))
    dm=Nodes('testsql.sqlite')
    try:
        dm.Connect()
        dm.CreateTable()
        dm.AddCartesian(nodes)
    finally:
        dm.Close()

    