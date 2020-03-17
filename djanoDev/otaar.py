#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 14:45:30 2020

@author: knowlesjt
"""

import mysql.connector as mariadb

#connecting to mariadb server
mariadb_connection = mariadb.connect(user='root', password=input("Enter your Password: "), database='otaar')
cursor = mariadb_connection.cursor()

#making initial table, assessing total columns, making first column
tableName = input("Insert Table name: ")
columnNumber = float(input("Enter total number of columns: "))
columnName = input("Column Name: ")
columnType = input("Insert value type: ")
null = input("null or not null: ")
cursor.execute("CREATE TABLE {0}({1} {2} {3});".format(tableName, columnName, columnType, null))
mariadb_connection.commit()

#looping rest of the colomns until complete
#while columnNumber >= 1 do this shit below
length = 1
while columnNumber > length:
    length += 1

    icolumnName = input("Column Name: ")
    icolumnType = input("Insert value type: ")
    inull = input("null or not null: ")
    cursor.execute("ALTER TABLE {0} ADD ({1} {2} {3});".format(tableName, icolumnName, icolumnType, inull))
    mariadb_connection.commit()

#printing whatever you want
cursor.execute("show tables")

myresult = cursor.fetchall()
  
for x in myresult:
  print(x) 