#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 16:42:00 2019

@author: hollidayhp
"""

from io import StringIO
import re, shutil

def read_dump(dump_filename, target_table):
    sio = StringIO()

    read_mode = 0 # 0 - skip, 1 - header, 2 - data
    with open(dump_filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith('insert') and target_table in line:
                read_mode = 2
            if line.lower().startswith('create table') and target_table in line:
                read_mode = 1
                continue

            if read_mode==0:
                continue

            # Filling up the headers
            elif read_mode==1:
                if line.lower().startswith('primary'):
                    # add more conditions here for different cases 
                    #(e.g. when simply a key is defined, or no key is defined)
                    read_mode=0
                    sio.seek(sio.tell()-1) # delete last comma
                    sio.write('\n')
                    continue
                colheader = re.findall('`([\w_]+)`',line)
                for col in colheader:
                    sio.write(col.strip())
                    sio.write(',')

            # Filling up the data -same as @firelynx's code
            elif read_mode ==2:
                data = re.findall('\([^\)]*\)', line)
                try:
                    # ...
                except IndexError:
                    pass
                if line.endswith(';'):
                    break
    sio.seek(0)
    with open (target_table+'.csv', 'w') as fd:
        shutil.copyfileobj(sio, fd,-1)
    return # or simply return sio itself

def find_tables(dump_filename):
    table_list=[]

    with open(dump_filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith('create table'):
                table_name = re.findall('create table `([\w_]+)`', line.lower())
                table_list.extend(table_name)

    return table_list

def main():
    try:
        if len(sys.argv)>=2 and os.path.isfile(sys.argv[1]):
            if len(sys.argv)==2:
                print('Table name not provided, looking for all tables...')
                table_list = find_tables(sys.argv[1])
                if len(table_list)>0:
                    print('Found tables: ',str(table_list))
                    for table in table_list:
                        read_dump(sys.argv[1], table)
            elif len(sys.argv)==3:
                read_dump(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()