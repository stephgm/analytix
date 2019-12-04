#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:08:41 2019

@author: klinetry
"""


import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

import numpy as np

givencolor = 'orange'
derivedcolor = 'purple'


def showSlaved(scale = 2):
    fig,ax = plt.subplots(figsize=(10,10))
    ax.set_title('Slaved Rectangle')
    
    angle = 30
    rad = np.deg2rad(angle)
    
    x = np.cos(rad)
    y = np.sin(rad)
    
    h = y*scale
    w = x*scale
    
    # bearing and angle ring
    ax.add_patch(patches.Circle((0,0),radius = scale,fill=False,color='r'))
    ax.plot([0,0],[-scale,scale],color='r')
    ax.plot([-scale,scale],[0,0],color='r')
    ax.annotate('0',[0,scale],color='b')
    ax.annotate('90',[scale,0],color='b')
    ax.annotate('180',[0,-scale],color='b')
    ax.annotate('270',[-scale,0],color='b')
    ax.annotate('0',[scale,.1*scale],color='g')
    ax.annotate('90',[.1*scale,scale],color='g')
    ax.annotate('180',[-scale,.1*scale],color='g')
    ax.annotate('270',[.1*scale,-scale],color='g')
    
    # Show Givens
    ax.add_patch(patches.Circle((0,0), radius = .03*scale,color=givencolor))
    ax.plot([0,w],[0,0],color=givencolor)
    ax.plot([w,w],[0,h],color=givencolor)
    
    widthoffsets = -.2*scale
    ax.annotate('Width', xy=[w/2,.5*widthoffsets], xytext=[w/2,widthoffsets], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(w/2,widthoffsets,0,-widthoffsets)
    ax.annotate('Height', xy=[w+.5*widthoffsets,h/2],xytext=[w+widthoffsets,h/2],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square',fc='white'),color=givencolor)
    plt.arrow(w+widthoffsets,h/2,-widthoffsets,0)
    ax.annotate('Lat,Lon', xy=[-.4*scale,-.2*scale], xytext=[-.2*scale,-.1*scale], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(-.2*scale,-.1*scale,.2*scale,.1*scale)
    
    # Derived Quantities
    
    ax.add_patch(patches.Arc([0,0], .4*scale, .4*scale, 0,0,angle,color=derivedcolor))
    ax.annotate('Math Angle',xy = [.35*scale,.05*scale],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square', fc='white'),color=derivedcolor)
    ax.add_patch(patches.Circle([w,h], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([-w,h], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([w,-h], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([-w,-h], radius = .01*scale,color=derivedcolor))
    ax.plot([0,x*scale],[0,y*scale],color=derivedcolor)
    ax.plot([0,-x*scale],[0,y*scale],color=derivedcolor)
    ax.plot([0,-x*scale],[0,-y*scale],color=derivedcolor)
    ax.plot([0,x*scale],[0,-y*scale],color=derivedcolor)
    ax.annotate('Bearing 1:\n90 - Math Angle',[w/2-.2*scale,h/2+.1*scale],color=derivedcolor)
    ax.annotate('Bearing 2:\n90 + Math Angle',[w/2-.2*scale,-h/2-.1*scale],color=derivedcolor)
    ax.annotate('Bearing 3:\n270 - Math Angle',[-w/2,-h/2-.1*scale],color=derivedcolor)
    ax.annotate('Bearing 4:\n270 + Math Angle',[-w/2,h/2],color=derivedcolor)
    
    # result
    ax.add_patch(patches.Rectangle([-w,-h], 2*w, 2*h, color='g',ls='--',alpha=0.2))
    
    legend_elements = [Line2D([0], [0], color=derivedcolor, lw=4, label='Derived Quantities'),
                       Line2D([0], [0], color=givencolor, label='Given Quantities'),
                       Line2D([0], [0], color='g', label='Result')]

    ax.legend(handles=legend_elements, loc='best').set_draggable(True)
    
    ax.set_aspect('equal')
    plt.show()
    
def showSlanted(scale = 2):
    fig,ax = plt.subplots(figsize=(10,10))
    ax.set_title('Slanted Rectangle')
    
    
    w = scale
    h = scale
    x = .5
    y = 1
    angle = np.rad2deg(np.arctan2(h,w/2))
    
    # bearing and angle ring
    ax.add_patch(patches.Circle((0,0),radius = scale,fill=False,color='r'))
    ax.plot([0,0],[-scale,scale],color='r')
    ax.plot([-scale,scale],[0,0],color='r')
    ax.annotate('0',[0,scale],color='b')
    ax.annotate('90',[scale,0],color='b')
    ax.annotate('180',[0,-scale],color='b')
    ax.annotate('270',[-scale,0],color='b')
    ax.annotate('0',[scale,.1*scale],color='g')
    ax.annotate('90',[.1*scale,scale],color='g')
    ax.annotate('180',[-scale,.1*scale],color='g')
    ax.annotate('270',[.1*scale,-scale],color='g')
    
    # given quatities
    ax.add_patch(patches.Circle((0,0), radius = .03*scale,color=givencolor))
    ax.plot([-w/2,w/2],[0,0],color=givencolor,lw=3)
    ax.plot([0,0],[0,h],color=givencolor,lw=3)
    
    widthoffsets = -.2*scale
    ax.annotate('Width', xy=[0,.5*widthoffsets], xytext=[0,widthoffsets], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(0,widthoffsets,0,-widthoffsets)
    ax.annotate('Height', xy=[.5*widthoffsets,h/2],xytext=[widthoffsets,h/2],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square',fc='white'),color=givencolor)
    plt.arrow(widthoffsets,h/2,-widthoffsets,0)
    ax.annotate('Lat,Lon', xy=[-.4*scale,-.2*scale], xytext=[-.2*scale,-.1*scale], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(-.2*scale,-.1*scale,.2*scale,.1*scale)
    
    # Derived Quantities
    ax.add_patch(patches.Arc([0,0], .4*scale, .4*scale, 0,0,angle,color=derivedcolor))
    ax.annotate('Math Angle',xy = [.35*scale,.05*scale],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square', fc='white'),color=derivedcolor)
    ax.add_patch(patches.Circle([w/2,h], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([-w/2,h], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([w/2,0], radius = .01*scale,color=derivedcolor))
    ax.add_patch(patches.Circle([-w/2,0], radius = .01*scale,color=derivedcolor))
    ax.plot([0,x*scale],[0,y*scale],color=derivedcolor)
    ax.plot([0,-x*scale],[0,y*scale],color=derivedcolor)
    ax.plot([0,-x*scale],[0,0],color=derivedcolor)
    ax.plot([0,x*scale],[0,0],color=derivedcolor)
    ax.annotate('Bearing 1:\n90 - Math Angle',[w/2-.1*scale,h/2+.1*scale],color=derivedcolor)
    ax.annotate('Bearing 2: 90',[w/2-.2*scale,-.1*scale],color=derivedcolor)
    ax.annotate('Bearing 3: 270',[-w/2,.1*scale],color=derivedcolor)
    ax.annotate('Bearing 4:\n270 + Math Angle',[-w/2-.2*scale,h/2],color=derivedcolor)
    
    # result
    ax.add_patch(patches.Rectangle([-w/2,0], w, h,  color='g',ls='--',alpha=0.2))
    
    legend_elements = [Line2D([0], [0], color=derivedcolor, lw=4, label='Derived Quantities'),
                       Line2D([0], [0], color=givencolor, label='Given Quantities'),
                       Line2D([0], [0], color='g', label='Result')]

    ax.legend(handles=legend_elements, loc='best').set_draggable(True)
    
    ax.set_aspect('equal')
    plt.show()
    
    
def showCircle(scale=3):
    fig,ax = plt.subplots(figsize=(10,10))
    ax.set_title('Circle')
    
    
    # bearing and angle ring
    ax.add_patch(patches.Circle((0,0),radius = scale,fill=False,color='r'))
    ax.plot([0,0],[-scale,scale],color='r')
    ax.plot([-scale,scale],[0,0],color='r')
    ax.annotate('0',[0,scale],color='b')
    ax.annotate('90',[scale,0],color='b')
    ax.annotate('180',[0,-scale],color='b')
    ax.annotate('270',[-scale,0],color='b')
    ax.annotate('0',[scale,.1*scale],color='g')
    ax.annotate('90',[.1*scale,scale],color='g')
    ax.annotate('180',[-scale,.1*scale],color='g')
    ax.annotate('270',[.1*scale,-scale],color='g')
    
    # given quatities
    ax.add_patch(patches.Circle((0,0), radius = .03*scale,color=givencolor))
    ax.plot([scale,scale],[0,0],color=givencolor,lw=3)
    
    widthoffsets = -.2*scale
    ax.annotate('Radius', xy=[.5*widthoffsets,scale/2],xytext=[widthoffsets,scale/2],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square',fc='white'),color=givencolor)
    plt.arrow(widthoffsets,scale/2,-widthoffsets,0)
    ax.annotate('Lat,Lon', xy=[-.4*scale,-.2*scale], xytext=[-.2*scale,-.1*scale], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(-.2*scale,-.1*scale,.2*scale,.1*scale)
    
    # result
    ax.add_patch(patches.Circle([0,0], radius=scale, color='g',ls='--',alpha=0.2))
    
    legend_elements = [Line2D([0], [0], color=givencolor, label='Given Quantities'),
                       Line2D([0], [0], color='g', label='Result')]

    ax.legend(handles=legend_elements, loc='best').set_draggable(True)
    
    ax.set_aspect('equal')
    plt.show()
    
def showEllipse(scale=3):
    fig,ax = plt.subplots(figsize=(10,10))
    ax.set_title('Ellipse')
    
    
    w = scale
    h = scale*.3
    x = .5
    y = 1
    angle = np.rad2deg(np.arctan2(h,w/2))
    
    # bearing and angle ring
    ax.add_patch(patches.Circle((0,0),radius = scale,fill=False,color='r'))
    ax.plot([0,0],[-scale,scale],color='r')
    ax.plot([-scale,scale],[0,0],color='r')
    ax.annotate('0',[0,scale],color='b')
    ax.annotate('90',[scale,0],color='b')
    ax.annotate('180',[0,-scale],color='b')
    ax.annotate('270',[-scale,0],color='b')
    ax.annotate('0',[scale,.1*scale],color='g')
    ax.annotate('90',[.1*scale,scale],color='g')
    ax.annotate('180',[-scale,.1*scale],color='g')
    ax.annotate('270',[.1*scale,-scale],color='g')
    
    # Show Givens
    ax.add_patch(patches.Circle((0,0), radius = .03*scale,color=givencolor))
    ax.plot([0,w],[0,0],color=givencolor)
    ax.plot([0,0],[0,h],color=givencolor)
    
    widthoffsets = -.2*scale
    ax.annotate('Minor', xy=[w/2,.5*widthoffsets], xytext=[w/2,widthoffsets], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(w/2,widthoffsets,0,-widthoffsets)
    ax.annotate('Major', xy=[.5*widthoffsets,h/2],xytext=[widthoffsets,h/2],
                ha='center', va='bottom',
                bbox=dict(boxstyle='square',fc='white'),color=givencolor)
    plt.arrow(widthoffsets,h/2,-widthoffsets,0)
    ax.annotate('Lat,Lon', xy=[-.4*scale,-.2*scale], xytext=[-.2*scale,-.1*scale], 
            ha='center', va='bottom',
            bbox=dict(boxstyle='square', fc='white'),color=givencolor)
    plt.arrow(-.2*scale,-.1*scale,.2*scale,.1*scale)
    
    # result
    ax.add_patch(patches.Ellipse([0,0], w*2, h*2, color='g',ls='--',alpha=0.2))
    
    legend_elements = [Line2D([0], [0], color=givencolor, label='Given Quantities'),
                       Line2D([0], [0], color='g', label='Result')]

    ax.legend(handles=legend_elements, loc='best').set_draggable(True)
    
    ax.set_aspect('equal')
    plt.show()
    
if __name__ == '__main__':
    showSlanted()   
    showSlaved()
    showCircle()
    showEllipse()
    
    