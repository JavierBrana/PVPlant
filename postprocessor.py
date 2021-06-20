# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- textures on nurbs use cases heights and sun intensity
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


import numpy as np
import geodat
import time
import cv2
import matplotlib



def getHeights(nsf,size=16):

	kzs=np.zeros((size+1,size+1),np.float)
	for ux in range(size+1):
		for vx in range(size+1):
			u=float(ux)/size
			v=float(vx)/size
			p=nsf.value(u,v)
			kzs[ux,vx]=p[2]

	kzs *= 0.001

	# normalize
	kzs -= kzs.min()
	kzs /= kzs.max()
	return kzs


def getNormals(nsf,size=16,direction=FreeCAD.Vector(0,0,1)):

	direction.normalize()
	kzs=np.zeros((size+1,size+1),np.float)
	for ux in range(size+1):
		for vx in range(size+1):
			u=float(ux)/size
			v=float(vx)/size
			(t1,t2)=nsf.tangent(u,v)
			# calculate the normale vector and how it differs from the given direction
			n=t1.cross(t2)
			kzs[ux,vx]=n*direction

	return kzs




def createColor(kzs,size,mode):

	img= np.zeros((size+1,size+1,3), np.uint8)

	#cmap = matplotlib.cm.get_cmap('jet')
	cmap = matplotlib.cm.get_cmap('hsv')

	for ux in range(size+1):
		for vx in range(size+1):
			t=kzs[ux,vx]
			if mode == 1: (r,g,b,a)=cmap(1-t)
			if mode == 2: (r,g,b,a)=cmap(t)
			img[size-vx,size-ux]=(255*r,255*g,255*b)

#	cv2.applyColorMap(img, cv2.COLORMAP_JET)

	#cv2.imshow('image2',img)
	fn='/tmp/image_'+str(size)+'.png'
	cv2.imwrite(fn,img)
	return fn

#
#
# use cases
#


nurbs=App.ActiveDocument.QuadNurbs



'''
#
# Height map
#

s=64

kzs=getHeights(nurbs.Shape.Surface,s)
fn=createColor(kzs,s,1)
geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
Gui.updateGui()
App.ActiveDocument.Text.LabelText=["Height Map","colormap HSV",str(s**2) + " color pixel"]

'''

'''
#
#  Height map animation with different solutions
#

for s in 4,8,16,32:
	kzs=getHeights(nurbs.Shape.Surface,s)
	fn=createColor(kzs,s,1)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()
	time.sleep(0.4)
'''

'''
#
# How planar is the surface - normals
#

for s in 4,8,16,32,64,256:
	kzs=getNormals(nurbs.Shape.Surface,s)
	fn=createColor(kzs,s,1)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()
	time.sleep(0.4)
'''


#
# flow of the sun from 6:00 a.m. until 6:00 p.m. in 60 steps
#

for h in range(61):
	s=100

	App.ActiveDocument.Text.LabelText=["Simulation Sun, Day time",str(6.0+ 12.0*h/60),str(s**2) + " color pixel"]

	kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(np.cos(np.pi*h/60),-np.sin(np.pi*h/60),np.sin(np.pi*h/60)))

	# evening sun
	# kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(-1,-1,2-0.05*h))

	# from axo view
	# kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(1,-1,2-0.05*h))

	fn=createColor(kzs,s,2)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()
