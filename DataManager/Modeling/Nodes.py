# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 16:32:51 2016

@author: huan
"""

import pandas as pd

    
def CreateTable(conn):
    sql='CREATE TABLE IF NOT EXISTS Node_Coordinates(\
    Name TEXT UNIQUE PRIMARY KEY, \
    CoordSys TEXT, \
    CoordType TEXT, \
    X REAL, \
    Y REAL, \
    Z REAL)'
    cu=conn.cursor()
    cu.execute(sql)
    cu.close()
    
def AddCartesian(conn,nodes):
    """
    conn: sqlite database connection
    nodes: a list of tuples in (name,x,y,z)
    """
    cu=conn.cursor()
    sql='INSERT INTO Node_Coordinates VALUES (?,?,?,?,?,?)'
    args=[]
    for node in nodes:
        args.append((str(node[0]),'Global','Cartesian',str(node[1]),str(node[2]),str(node[3])))
    cu.executemany(sql,args)
    conn.commit()
    cu.close()
            
def Count():
    return False
    
def GetCoordCartesian():
    return False
        

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

    