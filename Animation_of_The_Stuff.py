# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 20:50:21 2019

@author: Jordan
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.animation import FuncAnimation
fig = plt.figure()
ax = fig.gca(projection='3d')

#Boolean value to see the different animations.
# Roll = True shows roll animation of 360 degrees
# Roll = False shows yaw animation of 360 degrees
Roll = True

#Thingy1 Vector from origin
Tvec = np.array([20,20,19])
#Thingy2 Vector from origin
Ivec = np.array([2,2,5])
#Vector from Thingy1 to Thingy2
TIvec = Tvec-Ivec

#This is the New X axis unit vector after orientation of Thingy2
#I just made one up, but you have found this using the first row of the matrix
NewXunit = np.array([3**(-.5)]*3)

#This is the New Y axis vector.  Here I'm using Gram-Schmidt process to make sure
#that it is orthogonal to the New X axis.  Again, you can find this from the 
#second row of the matrix
NewY = np.array([0,-1,0]) - NewXunit*np.dot(np.array([0,-1,0]),NewXunit)

#Now I need to just make it a unit Vector
NewYunit = NewY/np.linalg.norm(NewY)

#Now just for completion I find the New Z Axis.  This can be found from the 
#third row of the matrix.  (It is uneeded, but would be useful for checking correctness)
NewZunit = np.cross(NewXunit,NewYunit)

#Adding the Vector to Thingy1 to the plot
ax.quiver(0,0,0,Tvec[0],Tvec[1],Tvec[2],color='green')

#Adding the Vector to Thingy2 to the plot
ax.quiver(0,0,0,Ivec[0],Ivec[1],Ivec[2],color='blue')

#Adding the Vector between Thingy1 to Thingy2
ax.quiver(Ivec[0],Ivec[1],Ivec[2],TIvec[0],TIvec[1],TIvec[2],color='purple')

#Adding the New X Axis unit Vector to the plot at the current location of Thingy2
ax.quiver(Ivec[0],Ivec[1],Ivec[2],NewXunit[0],NewXunit[1],NewXunit[2],color='teal')

#Adding the New Y Axis unit Vector to the plot at the current location of Thingy2
ax.quiver(Ivec[0],Ivec[1],Ivec[2],NewYunit[0],NewYunit[1],NewYunit[2],color='black')

#Adding the New Z Axis unit Vector to the plot at the current location of Thingy2
ax.quiver(Ivec[0],Ivec[1],Ivec[2],NewZunit[0],NewZunit[1],NewZunit[2],color='red')

#Adding the New -Y Axis unit Vector to the plot at the current location of Thingy2
#This is added to help visualize what the angle from the New Y Axis Should be.
ax.quiver(Ivec[0],Ivec[1],Ivec[2],-NewYunit[0],-NewYunit[1],-NewYunit[2],color='grey')

#Now we only need the New Y-Z components of the the Vector between Thingy1 and Thingy2
#So I just project the Vector into the plane created by the NewY NewZ unit vectors. NewX is the normal vector.
projectedTIvec = TIvec - NewXunit*np.dot(TIvec,NewXunit)

#Adding the projected vector to the plot.  This will help visualize at what angle the vector is from the black axis
ax.quiver(Ivec[0],Ivec[1],Ivec[2],projectedTIvec[0],projectedTIvec[1],projectedTIvec[2],color='yellow')

#Adding the New -Z Axis unit Vector to the plot at the current location of Thingy2
#This is added to help visualize what the angle from the New Y Axis Should be.
ax.quiver(Ivec[0],Ivec[1],Ivec[2],-NewZunit[0],-NewZunit[1],-NewZunit[2],color='orange')

#Calculating the angle from the boresight (You have already done this.)
boresightangle = np.rad2deg(np.arccos(np.dot(TIvec,NewXunit)/(np.linalg.norm(TIvec))))

#Used to scale the x,y,z axes of the plot so that the Vectors actually look orthogonal
#and to scale with one another
ax.auto_scale_xyz([0, 10], [0, 10], [0, 10])


#Here we are finding the angle from the Y-Z projected Thingy1-Thingy2 Vector
#with respect to the New Y Axis unit vector

#The determinent will take out any ambiguity of the angle, since arccos of a dot product
#will only return an angle between 0 - 180 degrees.
det = np.linalg.det([[1.,1.,1.], NewYunit ,projectedTIvec])
        
#Getting the full counter-clockwise angle
angle = np.rad2deg(np.arccos(np.dot(NewYunit ,projectedTIvec)/(np.linalg.norm(projectedTIvec))))
if det < 0:
    angle = 360 - angle
else:
    angle = angle

#I'm printing the angle
print(angle)

#Making a new plot
fig = plt.figure()
ax = fig.gca()

#Creating a patch that will display the area in which Thingy1 needs to be visible
boresight = plt.Circle((0,0),radius=2, color = 'g')
#Add the patch to the axes
ax.add_artist(boresight)

#This is just visualization of the circle that you are able to create currently
#Making a linspacing for the X coordinates 
circlexs = np.linspace(-boresightangle,boresightangle,1000)
#Making the top half of the circle (A circle is not a function so it cannot be plotted in one go)
topcircys = np.sqrt(boresightangle**2 - circlexs**2)
#Bottom half of the circle
botcircys = -topcircys

#Here is the line that can be made using the angle between the New Y Axis unit vector
#and the projected Thingy1-Thingy2 Vector.  I use Sine and Cosine to take out any ambiguity.
#The boresightangle multiplication is just the length of that line.  Just long enough to kiss
#the circle.  And of course you want to draw this line from the origin, hence the (0,0)
AngleLinexs = [0,boresightangle*np.cos(np.deg2rad(angle))]
AngleLineys = [0,boresightangle*np.sin(np.deg2rad(angle))]

#Here is how you would get the point of where Thingy1 is with respect to Thingy2's line
#of sight.
PointIntersectionX = [boresightangle*np.cos(np.deg2rad(angle))]
PointIntersectionY = [boresightangle*np.sin(np.deg2rad(angle))]

#Plot Everything
ax.plot(circlexs,topcircys)
ax.plot(circlexs,botcircys)
ax.plot(AngleLinexs,AngleLineys)
ax.scatter(PointIntersectionX,PointIntersectionY,s=20,c='r')

#Set the aspect ratio... God forbid the circle doesn't look like a circle.
ax.set_aspect('equal')


circlex = []
topcircy=[]
botcircy=[]
pointintersecx = []
pointintersecy = []

#This for loop will illustrate a Roll in the counter-clockwise direction by 360 degrees
#That is to say, that the rotation will be about the New X axis
if Roll:
    for i in range(361):
        j = float(i)
        # Setting up easy cosine and sine variables
        c, s = np.cos(np.deg2rad(j)), np.sin(np.deg2rad(j))
        
        #This is the rotation matrix about the New X Axis (This is an arbitrary Axis rotation matrix in 3D)
        #To rotate about another axis change NewXunit to some other vector (later Ill do one about the New Z axis)
        RnewXaxis = np.array(((c+(NewXunit[0]**2)*(1.0-c), NewXunit[0]*NewXunit[1]*(1.0-c)-NewXunit[2]*s, NewXunit[0]*NewXunit[2]*(1.0-c)+NewXunit[1]*s),\
                              (NewXunit[0]*NewXunit[1]*(1.0-c)+NewXunit[2]*s,c+(NewXunit[1]**2)*(1.0-c), NewXunit[1]*NewXunit[2]*(1.0-c)-NewXunit[0]*s),\
                              (NewXunit[0]*NewXunit[2]*(1.0-c)-NewXunit[1]*s,NewXunit[2]*NewXunit[1]*(1.0-c)+NewXunit[0]*s,c+(NewXunit[2]**2)*(1.0-c)))) 
        
        #This is the new position of the rotated Y axis. Note: We should rotate the Z axis too, however, it is not used in any calculation so who cares?
        # When I rotate about the Z axis later, we will have to rotate the X and the Y axes because they are both used to calculate things.
        roty = np.matmul(RnewXaxis,NewYunit)
        
        #This determinant will help solve any ambiguity to what the angle is Arccos will only give the smallest angle
        # we need the full counter-clockwise angle from the Y axis
        det = np.linalg.det([[1.,1.,1.],roty ,projectedTIvec])
        
        #Getting the full counter-clockwise angle
        dotproduct = np.dot(roty ,projectedTIvec)/(np.linalg.norm(projectedTIvec))
        #This dot product should never be greater than 1 or less than -1, but due to floating point division it sometimes barely misses the mark.
        if dotproduct > 1.0:
            dotproduct = 1.0
        if dotproduct < -1.0:
            dotproduct = -1.0
        angle1 = np.rad2deg(np.arccos(dotproduct))
        if det < 0:
            angles = 360 - angle1
        else:
            angles = angle1
        
        #Re calculate the boresight angle (This will always be the same for a Roll rotation because neither Thingy1 or Thingy2's
        #positions are changing, but I do it anyway)
        boresights = (np.rad2deg(np.arccos(np.dot(TIvec,NewXunit)/(np.linalg.norm(TIvec)))))
        
        #Get the circle x points
        circlex.append(np.linspace(-boresights,boresights,1000))
        #Get the top half of the circl
        topcircy.append(np.sqrt(boresights**2 - circlex[-1]**2))
        
        #Get the point of intersection of the angle line and the boresight circle
        pointintersecx.append(boresights*np.cos(np.deg2rad(angles)))
        pointintersecy.append(boresights*np.sin(np.deg2rad(angles)))
        
    #Just getting the bottom half of the circle
    botcircy = -1*np.array(topcircy)
    
    #Animation of the roll.  1 degree per frame
    fig, ax = plt.subplots()
    lns = [plt.plot([],[],'go')[0],plt.plot([],[],'b')[0],plt.plot([],[],'orange')[0]]
    
    def init():
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        return lns
    
    def update(frame):
    
        lns[0].set_data(pointintersecx[frame],pointintersecy[frame])
        lns[1].set_data(circlex[frame],topcircy[frame])
        lns[2].set_data(circlex[frame],botcircy[frame])
        
        return lns
    
    ani = FuncAnimation(fig, update, frames=np.arange(0, 360, 1),
                        init_func=init, blit=True)
    ax.set_aspect('equal')
    plt.show()


if not Roll:
    circlex1 = []
    topcircy1=[]
    botcircy1=[]
    pointintersecx1 = []
    pointintersecy1 = []
    
    #This for loop illustrates a yaw axis rotation.  
    #That is to say it will rotate around the new Z axis.
    #We expect that the the absolute maximum boresight angle would be 180 degrees because we are turning all the way around,
    #however, that would only be the case if the Thingy1 was along the Thingy2's Y axis, so we should expect something close to 180 degrees.
    #Also, since Thingy2 is not looking directly at Thingy1 the dot should move around the circle
    
    for i in range(361):
        j = float(i)
        # Setting up easy cosine and sine variables
        c, s = np.cos(np.deg2rad(j)), np.sin(np.deg2rad(j))
        
        #This is the rotation matrix about the New Z Axis
        RnewZaxis = np.array(((c+(NewZunit[0]**2)*(1.0-c), NewZunit[0]*NewZunit[1]*(1.0-c)-NewZunit[2]*s, NewZunit[0]*NewZunit[2]*(1.0-c)+NewZunit[1]*s),\
                              (NewZunit[0]*NewZunit[1]*(1.0-c)+NewZunit[2]*s,c+(NewZunit[1]**2)*(1.0-c), NewZunit[1]*NewZunit[2]*(1.0-c)-NewZunit[0]*s),\
                              (NewZunit[0]*NewZunit[2]*(1.0-c)-NewZunit[1]*s,NewZunit[2]*NewZunit[1]*(1.0-c)+NewZunit[0]*s,c+(NewZunit[2]**2)*(1.0-c))))
        
        
        #This is the new position of the rotated Y and X axes.
        roty = np.matmul(RnewZaxis,NewYunit)
        rotx = np.matmul(RnewZaxis,NewXunit)
        
        #We need to reproject the Thingy1-Thingy2 vector into the new Plane every time the axes change
        projectedTIvec = TIvec - rotx*np.dot(TIvec,rotx)
        
        
        #This determinant will help solve any ambiguity to what the angle is Arccos will only give the smallest angle
        # we need the full counter-clockwise angle from the rotated Y axis
        det = np.linalg.det([[1.,1.,1.],roty ,projectedTIvec])
        
        #Getting the full counter-clockwise angle
        angley = np.rad2deg(np.arccos(np.dot(roty ,projectedTIvec)/(np.linalg.norm(projectedTIvec))))
        if det < 0:
            angles = 360 - angley
        else:
            angles = angley
            
        
        #Recalculate the boresight angle (This time it will change because our X axis is moving)
        boresights = (np.rad2deg(np.arccos(np.dot(TIvec,rotx)/(np.linalg.norm(TIvec)))))
        
        #Get the circle x points
        circlex1.append(np.linspace(-boresights,boresights,1000))
        #Get the top half of the circl
        topcircy1.append(np.sqrt(boresights**2 - circlex1[-1]**2))
        
        #Get the point of intersection of the angle line and the boresight circle
        pointintersecx1.append(boresights*np.cos(np.deg2rad(angles)))
        pointintersecy1.append(boresights*np.sin(np.deg2rad(angles)))
        
    #Just getting the bottom half of the circle
    botcircy1 = -1*np.array(topcircy1)
    
    #Animation of the roll.  1 degree per frame
    fig1, ax1 = plt.subplots()
    lns = [plt.plot([],[],'go')[0],plt.plot([],[],'b')[0],plt.plot([],[],'orange')[0]]
    
    def init1():
        ax1.set_xlim(-180, 180)
        ax1.set_ylim(-180, 180)
        return lns
    
    def update1(frame):
    
        lns[0].set_data(pointintersecx1[frame],pointintersecy1[frame])
        lns[1].set_data(circlex1[frame],topcircy1[frame])
        lns[2].set_data(circlex1[frame],botcircy1[frame])
        
        return lns
    
    ani = FuncAnimation(fig1, update1, frames=np.arange(0, 360, 1),
                        init_func=init1, blit=True)
    ax1.set_aspect('equal')
    plt.show()
