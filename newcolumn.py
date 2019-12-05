#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 22:56:58 2019

@author: Jordan
"""
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic

import os
import sys
import pandas as pd
import numpy as np
from six import string_types

import QtUtils

class ParseDataFrame(Widgets.QDialog):
    def __init__(self,parent=None,data=None,**kwargs):
        super(ParseDataFrame,self).__init__(parent)
        self.parent = parent
        self.data = data
        if not isinstance(self.data,pd.DataFrame):
            print('The data passed was not a dataframe')
            return
        self.headers = list(self.data)
        self.functions = ['cos','sin','tan','arccos','arcsin','arctan',
                          'cosh','sinh','tanh','arccosh','arcsinh','arctanh',
                          'pi','sqrt','exp','log','ln','log10','log2','abs',
                          'cumsum','rss','derivative']
        self.LastCursorPos = 0
        self.makeWidget()
        self.ParseLine.setFocus()
        self.makeConnections()
        self.makeToolBar()

    def makeConnections(self):
        self.HeaderList.getSelection.connect(self.addFieldToLine)
        self.FunctionList.getSelection.connect(self.addFunctionToLine)
        self.HeaderList.ListWidget.itemDoubleClicked.connect(self.addFieldToLine)
        self.FunctionList.ListWidget.itemDoubleClicked.connect(self.addFunctionToLine)
        self.ParseLine.cursorPositionChanged.connect(self.setLastCursorPos)

    def makeToolBar(self,**kwargs):
        #TODO make resourcedir with REL_LIB_PATH
        self.toolBar = Widgets.QToolBar()
        helptool = Widgets.QAction('Help',self)
        helptool.triggered.connect(self.get_help)
        self.toolBar.addAction(helptool)
        self.layout.setMenuBar(self.toolBar)

    def makeWidget(self,**kwargs):
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.HeaderNameLabel = Widgets.QLabel('New Column Name:')
        self.ColumnName = Widgets.QLineEdit('New_Column')
        self.ParseLineColLabel = Widgets.QLabel(self.ColumnName.text()+'=')
        self.ColumnName.textChanged.connect(lambda text:self.ParseLineColLabel.setText(text+'='))
        self.ParseLineLabel = Widgets.QLabel('Expression')
        self.ParseLine = Widgets.QLineEdit()
        self.HeaderList = QtUtils.StringListWidget(self.headers,self,selectAll=False,OKname='Add To Line')
        self.FunctionList = QtUtils.StringListWidget(self.functions,self,selectAll=False,OKname='Add To Line')
        self.layout.addWidget(self.HeaderNameLabel,0,0)
        self.layout.addWidget(self.ColumnName,0,1,1,5)
        self.layout.addWidget(self.ParseLineLabel,1,0,1,6)
        self.layout.addWidget(self.ParseLineColLabel,2,0)
        self.layout.addWidget(self.ParseLine,2,1,1,5)
        self.layout.addWidget(self.FunctionList,3,0,1,3)
        self.layout.addWidget(self.HeaderList,3,3,1,3)
        self.TestButton = Widgets.QPushButton('Show Evaluation')
        self.TestButton.clicked.connect(lambda trash:self.DoCalc())
        self.layout.addWidget(self.TestButton,4,2,1,2)
        self.AcceptButton = Widgets.QPushButton('Accept')
        self.AcceptButton.clicked.connect(lambda trash:self.Accept())
        self.layout.addWidget(self.AcceptButton,5,2,1,2)

    def keyPressEvent(self,e):
        e.ignore()

    def setLastCursorPos(self,x,y,**kwargs):
        self.LastCursorPos = (x,y)

    def addFieldToLine(self,items):
        if items:
            if isinstance(items,list):
                for item in items:
                    string = self.ParseLine.text()
                    string = string[:self.LastCursorPos[1]]+"['{}']".format(item)+string[self.LastCursorPos[1]:]
                    self.ParseLine.setText("{}".format(string))
            elif isinstance(items,Widgets.QListWidgetItem):
                string = self.ParseLine.text()
                string = string[:self.LastCursorPos[1]]+"['{}']".format(items.text())+string[self.LastCursorPos[1]:]
                self.ParseLine.setText("{}".format(string))
#                self.ParseLine.setText("{} ['{}']".format(self.ParseLine.text(),items.text()))
        self.ParseLine.setFocus()
        self.ParseLine.setCursorPosition(self.LastCursorPos[1])

    def addFunctionToLine(self,items):
        if items:
            if isinstance(items,list):
                for item in items:
                    string = self.ParseLine.text()
                    string = string[:self.LastCursorPos[1]]+"{}(".format(item)+string[self.LastCursorPos[1]:]
                    self.ParseLine.setText("{}".format(string))
#                    self.ParseLine.setText("{} {}(".format(self.ParseLine.text(),item))
            elif isinstance(items,Widgets.QListWidgetItem):
                string = self.ParseLine.text()
                string = string[:self.LastCursorPos[1]]+"{}(".format(items.text())+string[self.LastCursorPos[1]:]
                self.ParseLine.setText("{}".format(string))
#                self.ParseLine.setText("{} {}(".format(self.ParseLine.text(),items.text()))
        self.ParseLine.setFocus()
        self.ParseLine.setCursorPosition(self.LastCursorPos[1])

    def get_help(self,**kwargs):
        print('help')

    def DoCalc(self,**kwargs):
        test = kwargs.get('test',True)
        lines = self.ParseLine.text()
        lines = lines.replace(' ','').lower()
        if 'cos(' in lines:
            lines = lines.replace('cos(','np.cos(')
        if 'sin(' in lines:
            lines = lines.replace('sin(','np.sin(')
        if 'tan(' in lines:
            lines = lines.replace('tan(','np.tan(')
        if '^' in lines:
            lines = lines.replace('^','**')
        if 'arcsin(' in lines:
            lines = lines.replace('arcsin(','np.arcsin(')
        if 'arccos(' in lines:
            lines = lines.replace('arccos(','np.arccos(')
        if 'arctan(' in lines:
            lines = lines.replace('arctan(','np.arctan(')
        if 'cosh(' in lines:
            lines = lines.replace('cosh(','np.cosh(')
        if 'sinh(' in lines:
            lines = lines.replace('sinh(','np.sinh(')
        if 'tanh(' in lines:
            lines = lines.replace('tanh(','np.tanh(')
        if 'arcsinh(' in lines:
            lines = lines.replace('arcsinh(','np.arcsinh(')
        if 'arccosh(' in lines:
            lines = lines.replace('arccosh(','np.arccosh(')
        if 'arctanh(' in lines:
            lines = lines.replace('arctanh(','np.arctanh(')
        if 'pi' in lines:
            lines = lines.replace('pi','np.pi')
        if 'sqrt(' in lines:
            lines = lines.replace('sqrt(','np.sqrt(')
        if 'exp(' in lines:
            lines = lines.replace('exp(','np.exp(')
        if 'log(' in lines:
            lines = lines.replace('log(','np.log(')
        if 'ln(' in lines:
            lines = lines.replace('ln(','np.log(')
        if 'log10(' in lines:
            lines = lines.replace('log10(','np.log10(')
        if 'log2(' in lines:
            lines = lines.replace('log2(','np.log2(')
        if 'abs(' in lines:
            lines = lines.replace('abs(','np.abs(')
        if 'cumsum(' in lines:
            lines = lines.replace('cumsum(','np.cumsum(')

        if 'rss(' in lines:
            lines = lines.replace('rss(','self.RSS(')
        if 'derivative(' in lines:
            lines = lines.replace('derivative(','self.Derivative(')
        
        fieldTest = []
        for thing in self.data:
            fieldTest.append("['{}']".format(thing))
            if thing.lower() in lines:
                lines = lines.replace(thing.lower(),thing)
        for test in fieldTest:
            if test in lines:
                lines = lines.replace(test,'self.data'+test)
                
        x = pd.DataFrame()
        for i,line in enumerate(lines.split(';')):
            if 'if(' not in line:
                try:
                    x = eval(line)
                except:
                    print('Error in line {}'.format(i))
            else:
                try:
                    evalstring = line.split('if(')[-1].split(')=')
                    if isinstance(evalstring,list):
                        idx = eval(evalstring[0])
                        if x.shape[0]==0:
                            x = self.data[idx.name].copy()
                        x.loc[idx] = eval(line.split('=')[-1])
                except:
                    print('Error in line {}'.format(i))
        if (isinstance(x,(int,float,string_types)) or not len(x)):
            x = pd.Series([x]*self.data.shape[0])
        if test:
            text = str(x.to_list())
            window = Widgets.QLineEdit(text)
            window.show()
            print(x)
        else:
            return x
        # self.data = self.data.join(pd.Series(x,name=self.ColumnName.text()))
        # print(x)
    
    def RSS(self,*args):
        output = 0
        for arg in args:
            output += arg**2
        return np.sqrt(output)

    def Derivative(self,x):
        if isinstance(x,(int,float,string_types)):
            return 0
        return np.gradient(x,edge_order=2)

    def Accept(self,**kwargs):
        self.close()
        return self.DoCalc(test=False)



def main():
    y = {'This':[1,2,3,4,5],
         'That':[5,4,3,2,1]}
    y = pd.DataFrame(y)
    app = Widgets.QApplication(sys.argv)
    frame = ParseDataFrame(None,y)
    frame.show()
#    splash.finish(frame)
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
#    while time.time() < start+1:
#        app.processEvents()
    main()










