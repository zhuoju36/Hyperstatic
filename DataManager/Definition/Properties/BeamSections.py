# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 22:13:07 2016

@author: HZJ
"""

def CreateTable(conn):
    cu=conn.cursor()
    sqls=[]
    sqls.append(
    'CREATE TABLE IF NOT EXISTS Beam_Prop_General (\
    Name TEXT UNIQUE PRIMARY KEY, \
    Material TEXT, \
    Shape TEXT, \
    t3 REAL, \
    t2 REAL, \
    tf REAL, \
    tw REAL, \
    Area REAL, \
    TorsConst REAL, \
    I33 REAL, \
    I22 REAL, \
    AS2 REAL, \
    AS3 REAL, \
    S33 REAL, \
    S22 REAL, \
    Z33 REAL, \
    Z22 REAL, \
    R33 REAL, \
    R22 REAL, \
    Color TEXT, \
    FromFile INTEGER,\
    AMod REAL, \
    A2Mod REAL, \
    A3Mod REAL, \
    JMod REAL, \
    I2Mod REAL, \
    I3Mod REAL, \
    MMod REAL, \
    WMod REAL, \
    GUID TEXT, \
    Notes TEXT)'
    )

    for sql in sqls:
        cu.execute(sql)
    conn.commit()

def AddQuick(conn,material,profile):
    """
    profile: H400x200x10x12
    """
    cu=conn.cursor()
    if profile[0]=='H':
        size=profile[1:].split('x')
        rec=(
        profile,
        material,
        'I',
        str(size[0]),
        str(size[1]),
        str(size[3]),
        str(size[2]),
        0,#Area REAL, \
        0,#TorsConst REAL, \
        0,#I33 REAL, \
        0,#I22 REAL, \
        0,#AS2 REAL, \
        0,#AS3 REAL, \
        0,#S33 REAL, \
        0,#S22 REAL, \
        0,#Z33 REAL, \
        0,#Z22 REAL, \
        0,#R33 REAL, \
        0,#R22 REAL, \
        '0x000000',#Color TEXT, \
        0,#FromFile INTEGER,\
        0,#AMod REAL, \
        0,#A2Mod REAL, \
        0,#A3Mod REAL, \
        0,#JMod REAL, \
        0,#I2Mod REAL, \
        0,#I3Mod REAL, \
        0,#MMod REAL, \
        0,#WMod REAL, \
        '0',#GUID TEXT, \
        '0',#Notes TEXT
        )
        cu.execute('INSERT INTO Beam_Prop_General VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',rec)
    conn.commit()