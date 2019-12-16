# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 16:16:35 2019

@author: HollidayHP
"""
dbname = r'C:/tools/x.mdb'

from win32com.client import Dispatch

# datbase creation

try:
    accApp = Dispatch("Access.Application")
    dbEngine = accApp.DBEngine
    workspace = dbEngine.Workspaces(0)

    dbLangGeneral = ';LANGID=0x0409;CP=1252;COUNTRY=0'
    newdb = workspace.CreateDatabase(dbname, dbLangGeneral, 64)

    newdb.Execute("""CREATE TABLE Table1 (
                      ID autoincrement,
                      Col1 varchar(50),
                      Col2 double,
                      Col3 datetime);""")

except Exception as e:
    print(e)

finally:
    accApp.DoCmd.CloseDatabase
    accApp.Quit
    newdb = None
    workspace = None
    dbEngine = None
    accApp = None

import pyodbc

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+dbname+';')
cursor = conn.cursor()

def mdb_connect(db_file, user='admin', password = '', old_driver=False):
    driver_ver = '*.mdb'
    if not old_driver:
        driver_ver += ', *.accdb'

    odbc_conn_str = ('DRIVER={Microsoft Access Driver (%s)}'
                     ';DBQ=%s;UID=%s;PWD=%s' %
                     (driver_ver, db_file, user, password))

    return pyodbc.connect(odbc_conn_str)

conn = mdb_connect(dbname)  # only absolute paths