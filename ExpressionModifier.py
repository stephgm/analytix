# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 18:10:18 2018

@author: Jordan
"""

import numpy as np
import re

def parse(arglist):
    print 'arglist', arglist
    strings = arglist[0]
    indexes = arglist[1]
    z = arglist[2]
    v = np.copy(z)
    datasetReplace = []
    if len(strings) > 0:
        strings = strings+';z=v'
        strings = strings.replace(' ','')
        strings = strings.lower()
        if '^' in strings:
            strings = strings.replace('^','**')
        if 'cos(' in strings:
            strings = strings.replace('cos(','np.cos(')
        if 'sin(' in strings:
            strings = strings.replace('sin(','np.sin(')
        if 'tan(' in strings:
            strings = strings.replace('tan(','np.tan(')
        if 'arcsin(' in strings:
            strings = strings.replace('arcsin(','np.arcsin(')
        if 'arccos(' in strings:
            strings = strings.replace('arccos(','np.arccos(')
        if 'arctan(' in strings:
            strings = strings.replace('arctan(','np.arctan(')
        if 'cosh(' in strings:
            strings = strings.replace('cosh(','np.cosh(')
        if 'sinh(' in strings:
            strings = strings.replace('sinh(','np.sinh(')
        if 'tanh(' in strings:
            strings = strings.replace('tanh(','np.tanh(')
        if 'arcsinh(' in strings:
            strings = strings.replace('arcsinh(','np.arcsinh(')
        if 'arccosh(' in strings:
            strings = strings.replace('arccosh(','np.arccosh(')
        if 'arctanh(' in strings:
            strings = strings.replace('arctanh(','np.arctanh(')
        if 'pi' in strings:
            strings = strings.replace('pi','np.pi')
        if 'exp(' in strings:
            strings = strings.replace('exp(','np.exp(')
        if 'log(' in strings:
            strings = strings.replace('log(','np.log(')
        if 'ln(' in strings:
            strings = strings.replace('ln(','np.log(')
        if 'log10(' in strings:
            strings = strings.replace('log10(','np.log10(')
        if 'log2(' in strings:
            strings = strings.replace('log2(','np.log2(')
        if 'abs(' in strings:
            strings = strings.replace('abs(','np.abs(')
        if 'print' in strings:
            strings = strings.replace('print','print ')
        if 'all(' in strings and z.dtype.kind != 'S':
            strings = strings.replace('all(','z-z+(')
        if 'all(' in strings and z.dtype.kind == 'S':
            strings = strings.replace('all(','(')
        
        
        if '$' in strings:
            temp = 0
            varpos = [pos for pos, char in enumerate(strings) if char == '$']
            for i in varpos:
                datasetReplace.append(strings[i+1])
                if temp < strings[i+1]:
                    temp = strings[i+1]
            replaced = np.unique(datasetReplace)
            for i in replaced:
                strings = strings.replace('$'+i,str(float(i)-1.))
                
            if int(temp) > len(indexes):
                print "you have used", '$'+temp, "while the number of selected columns is", len(indexes)
                return
        lines = strings.split(';')
        i = 0
        executed = []
        for line in lines:
            i += 1
            if 'elif(' in line:
                line.replace('elif(','if(')
            if 'if(' in line:
                variable = 'v'
                line = line.replace('if(',variable + ' = np.where(')
                line = line.replace('):z=',',')

                line = line + ','+variable+')'
            if datasetReplace:
                for j in replaced:
                    line = line.replace(str(float(j)-1),'indexes['+str(int(j)-1)+']')
            try:
                exec(line)
                executed.append(str(i))
            except SyntaxError:
                if executed == []:
                    print 'Syntax error in line', str(i)+'.', 'No lines executed.'
                elif len(executed) == 1:
                    print 'Syntax error in line', str(i)+'.', 'Line',executed[-1], 'executed.'
                else:
                    executed.pop(-1)
                    if len(executed) == 1:
                        print('Syntax error in line ' +str(i)+'. Lines {0} and {1} executed properly.' .format(', '.join(executed),i-1))
                    else:
                        print('Syntax error in line ' +str(i)+'. Lines {0}, and {1} executed properly.' .format(', '.join(executed),i-1))
                return z
            except TypeError:
                if executed == []:
                    print 'Data Type error in line', str(i)+'.', 'No lines executed.'
                elif len(executed) == 1:
                    print 'Data Type error in line', str(i)+'.', 'Line',executed[-1], 'executed.'
                else:
                    executed.pop(-1)
                    if len(executed) == 1:
                        print('Data Type error in line ' +str(i)+'. Lines {0} and {1} executed properly.' .format(', '.join(executed),i-1))
                    else:
                        print('Data Type error in line ' +str(i)+'. Lines {0}, and {1} executed properly.' .format(', '.join(executed),i-1))
                return z
            except:
                if executed == []:
                    print 'Unrecognized error in line', str(i)+'.', 'No lines executed.'
                elif len(executed) == 1:
                    print 'Unrecognized error in line', str(i)+'.', 'Line',executed[-1], 'executed.'
                else:
                    executed.pop(-1)
                    if len(executed) == 1:
                        print('Unrecognized error in line ' +str(i)+'. Lines {0} and {1} executed properly.' .format(', '.join(executed),i-1))
                    else:
                        print('Unrecognized error in line ' +str(i)+'. Lines {0}, and {1} executed properly.' .format(', '.join(executed),i-1))
                return z
                
        print z
    


x = np.random.randint(128, size=10)
y = np.random.randint(128, size=10)
z = np.array([1,2,3,4,5,6,7,8,9,10])
a = np.array(['boo']*x.size)
b = np.array([True]*x.size)

string = 'printz;if(z<5):z=z+5;if(z>=5):z=z-5;'
path = '/blah' 
stringdict = {}
indecies = [x,y,a,b]
duplicate = z
for i in range(len(indecies)):
    dtype = indecies[i].dtype.kind
    if dtype != 'S' and dtype != 'b':
        indecies[i] = indecies[i].astype(float)
if z.dtype.kind == 'b':
    z = z.astype('|S')
if path not in stringdict:
    stringdict[path] = []
stringdict[path].append([string,indecies,duplicate])
stringdict[path].append([string,indecies,duplicate])

for i in range(len(stringdict[path])):
    parse(stringdict[path][i])
