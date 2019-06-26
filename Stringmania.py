# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 19:53:39 2019

@author: Jordan
"""
import re
import time

start = time.time()

string = "This      is a '   long ' 'string with this one  ' 'this should be taken care of' '            '    '               '  super  annoying spaces in 'between     '      'hey     '       '     '"
for quoted_part in re.findall(r"\'(.+?)\'", string):
    string = string.replace(quoted_part, quoted_part.replace(" ", ""))
#Replace whitespace in quotes after a word with just the word "'hello     '" -> "'hello'"
#newstring = re.sub(r"('(\s+|)[A-Za-z]+)[\s]{1,}'",r"\1'",string)
##Replace whitespace in quotes before a word with just the word "'     hello'" -> "'hello'"
#newstring = re.sub(r"'[\s]{1,}([A-Za-z]+')",r"'\1",newstring)
#Fix the empty quotes '' to ' '
newstring = re.sub(r"''",r"'   '",string)
##replace whitespace inside quotes
#newstring = re.sub(r"'([A-Za-z]+)\s+([A-Za-z]+)\s+'",r"'\1\2'",newstring)
#Replace multiple whitespace with one space "'     '" -> "' '"
newstring = re.sub(" +"," ",newstring)
newstring = re.sub(" ' '"," ' '  ",newstring)
#Make something unique to set the unwanted quotes to HHH is used.
newstring = re.sub(" ' ' "," HHH'   'HHH ",newstring)
#Replace quotes that have more than 2 spaces in them with the item you want
# HHH'        'HHH -> ' FML '
newstring = re.sub("HHH'  +'HHH",' FML ',newstring)
#Replace things with one ore more spaces with just one space
# The quick      brown    fox ->  The quick brown fox
newstring = re.sub(" +"," ",newstring)

#Get rid of the quotes finally
newstring = re.sub("'","",newstring)
#Split on the spaces
x = newstring.split()
for i,item in enumerate(x):
    if item == 'FML':
        x[i] = ''
print time.time() - start
