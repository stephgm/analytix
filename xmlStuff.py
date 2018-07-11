#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 11:33:14 2018

@author: hollidayh
"""

import os
import sys
import xml.etree.cElementTree as et
#from xml.dom import minidom
#import lxml.etree

data = {
'one':{'radius':10,'lat':40.,'lon':159.},
'two':{'radius':5.,'lat':45.,'lon':162.}}

xfile = '/home/hollidayh/Hamilton/src/python/xmlTest.xml'



def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

root = et.Element('root')

for x in data:
    nt = et.SubElement(root,x)
    nt.set('this','yo')
    nt.set('that','yoyo')
    for fld in data[x]:
        et.SubElement(nt,fld).text = str(data[x][fld])


tree = et.ElementTree(root)
indent(root)
tree.write(xfile)
# read / edit
tree = et.parse(xfile)
root = tree.getroot()
nt = et.SubElement(root,'three')
et.SubElement(nt,'lat').text = '70.0'
et.SubElement(nt,'lon').text = '145.0'
et.SubElement(nt,'radius').text = '12.0'
# remove existing data
for x in root.getchildren():
    if x.tag == 'one':
        root.remove(x)
#    else:
#        print(x.tag)
#        for y in x:
#            print('\t'+y.tag+' : '+y.text)
#            if x.tag == 'two' and y.tag == 'lat':
#                y.text = '55.0'
# edit existing data
for x in root.getchildren():
    if x.tag == 'two':
        for y in x.getchildren():
            if y.tag == 'lat':
                y.text = '55.0'
        for att in x.attrib:
            print(att+' : '+x.attrib[att])
indent(root)
tree.write(xfile)
