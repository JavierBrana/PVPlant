# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- create fake shadows -
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import Draft
import cProfile


def delo(obj):
		try:
			App.ActiveDocument.removeObject(obj.Name)
		except:
			print "schon geloescht"


def labelit(obj,label,fs=10,offset=(0,0,10),color=(1.0,1.0,1.0)):
	print obj.Name
	try: pos=obj.Shape.CenterOfMass
	except: 
		try: pos=obj.Shape.Compounds[0].Faces[0].CenterOfMass
		except: pos=obj.Placement.Base
	
	pos += FreeCAD.Vector(offset)
	import Draft
	l=Draft.makeText([label],pos)
	v=l.ViewObject
	v.FontSize = fs
	v.DisplayMode="Screen"
	v.TextColor= color 
	l.Label="# " + label

def showlab(l,offset=(0,0,0),color=(1.0,1.0,1.0)):
	objs=App.ActiveDocument.getObjectsByLabel(l)
	if objs<>[]:
		labelit(objs[0],l,offset=offset,color=color)

'''
showlab('Perspective shadow from Vector (1000.0, -450.0, 900.0)')
showlab("Bridge",(20,0,50),(1.0,1.0,0.0))
showlab("House",(20,0,50),(1.0,1.0,0.0))
showlab("Bottom")
'''


def createShadow(ground,ufo,mode='Parallel',groundIndex=None,ufoIndex=None,light=App.Vector(-1000,450,300)):


	if mode=="Perspective":
		Label="PointLight from "+str(light)
		l=App.ActiveDocument.getObjectsByLabel(Label)
		if l==[]:
			print "add light ",light
			sp=App.ActiveDocument.addObject("Part::Sphere","Sphere")
			sp.Placement.Base=light
			sp.ViewObject.ShapeColor=(1.0,1.0,0.0)
			sp.Radius=40
			sp.Label=Label
			showlab(Label,offset=(50,50,50))

	shs=[]
	goods=[]

	if ufoIndex==None:
		ufoIndex=range(len(ufo.Shape.Wires))

	if groundIndex==None:
		groundIndex=range(len(ground.Shape.Faces))

	print ufoIndex
	print groundIndex

	for w in ufoIndex:
		for fax in groundIndex:
			fa=ground.Shape.Faces[fax]
			if mode=="Perspective":
				proj=fa.makePerspectiveProjection(ufo.Shape.Wires[w],light)
			elif mode=="Parallel":
				proj=fa.makeParallelProjection(ufo.Shape.Wires[w],light)
			elif mode=="Cylindric":
				pass
			else:
				raise Exception("not implemented")


			if proj.Vertexes==[]: continue

			Part.show(proj)
			f=App.ActiveDocument.ActiveObject
			f.ViewObject.hide()

			r0=Draft.upgrade(f,delete=True)
			if r0[0]==[]:
#				print "loescehe",f.Label
#				s=f.Shape
#				for wi in s.Wires:
#					print wi
#					ww=Draft.makeWire(wi,closed=True)
#					print ww
#					goods.append(ww)
				delo(f)
			else:
				goods.append(App.ActiveDocument.ActiveObject)

			Gui.updateGui()

	# convert wires to faces
	i=0
	g3=[]

	while len(goods)>0 and i<5: 
		print ("i,goods ",i,len(goods))
		g2=[]
		i += 1
		for g in goods:
			try:
				if g.Name.startswith("Wire"):
					r0=Draft.upgrade(g,delete=True)
					if r0[0]==[]:
#						s=g.Shape
#						for wi in s.Wires:
#							print wi
#							ww=Draft.makeWire(wi,closed=True)
#							print ww
#							goods.append(ww)
						delo(g)
					else:
						g2.append(App.ActiveDocument.ActiveObject)
				if g.Name.startswith("Face"):
					 g3.append(g)
			except:
				pass
		goods=g2
		print ("unprocessed ",len(goods))

	shs=g3

	f=App.activeDocument().addObject("Part::MultiFuse","Fusion")
	f.Shapes= shs
	App.activeDocument().recompute()

	rc=App.ActiveDocument.addObject('Part::Feature','reduc')
	rc.Shape=f.Shape.removeSplitter()

	#clean up
	delo(f)
	for s in shs: delo(s)

	# darker shadow
	(r,g,b,t)=ground.ViewObject.ShapeColor
	rc.ViewObject.ShapeColor=(r*0.5,g*0.5,b*0.5,t)
	rc.ViewObject.DisplayMode = u"Shaded"

	Gui.updateGui()
	return rc

def createShadowSpace4(rc):
	''' hard coded shadow space methods'''

	ff=Draft.downgrade(rc,delete=False)
	faces=ff[0]
	f1=faces[0]
	f2=faces[1]
	App.ActiveDocument.recompute()
	a=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge3'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge3'])

	b=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge2'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge4'])

	c=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge1'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge1'])

	d=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge4'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge2'])
	App.ActiveDocument.recompute()

	_=Part.Shell([rc.Shape.Face1, rc.Shape.Face2, a.Shape.Face1, b.Shape.Face1, c.Shape.Face1, d.Shape.Face1, ])

	for oj in [a,b,c,d,f1,f2]:
		delo(oj)

	ss=App.ActiveDocument.addObject('Part::Feature','Shell')
	
	ss.Shape=_
	App.ActiveDocument.recompute()

	ss.ViewObject.ShapeColor=(1.0,1.0,0.0)
	ss.ViewObject.Transparency= 90
	ss.ViewObject.DisplayMode = u"Shaded"



def createShadowSpace5(rc):
	''' hard coded shadow space '''
	
	ff=Draft.downgrade(rc,delete=False)
	faces=ff[0]
	f1=faces[0]
	f2=faces[1]

	App.ActiveDocument.recompute()

	a=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge3'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge3'])

	b=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge2'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge4'])

	c=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge1'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge1'])

	d=FreeCAD.ActiveDocument.addObject('Part::RuledSurface', 'Ruled Surface')
	FreeCAD.ActiveDocument.ActiveObject.Curve1=(f1,['Edge4'])
	FreeCAD.ActiveDocument.ActiveObject.Curve2=(f2,['Edge2'])

	App.ActiveDocument.recompute()

	ss=App.ActiveDocument.addObject('Part::Feature','Shell')
	ss.Shape=Part.Shell([rc.Shape.Face1, rc.Shape.Face2, a.Shape.Face1, b.Shape.Face1, c.Shape.Face1, d.Shape.Face1, ])
	App.ActiveDocument.recompute()

	ss.ViewObject.ShapeColor=(1.0,1.0,0.0)
	ss.ViewObject.Transparency= 90
	ss.ViewObject.DisplayMode = u"Shaded"

	f2.ViewObject.ShapeColor=(1.0,1.0,0.0)
	f2.Placement.Base.z += 8
	f2.ViewObject.DisplayMode = u"Shaded"

	for oj in [a,b,c,d,f1]:
		delo(oj)

# -test cases


def test2():
	''' point light shadows of a bridge  '''

	ground=App.ActiveDocument.Body001
	ufo=App.ActiveDocument.Body

	for ll in [App.Vector(-1000,450,200),App.Vector(-1000,-450,500),App.Vector(1000,-450,900),App.Vector(700,1000,300)]:
		rc=createShadow(ufo=ufo,ground=ground,groundIndex=[5],mode='Perspective',light=ll)
		rc.Label="Perspective shadow from " +str(ll)
		showlab(rc.Label,offset=(0,0,10),color=(.7,1.0,0.7))


def test3():
	''' parallel light shadows of a bridge  '''

	ground=App.ActiveDocument.Body001
	ufo=App.ActiveDocument.Body

	for ll in [App.Vector(-1,1,1),App.Vector(-1000,-450,500),App.Vector(1000,-450,900),App.Vector(700,1000,300)]:
		rc=createShadow(ufo=ufo,ground=ground,groundIndex=[5],mode='Parallel',light=ll)
		rc.Label="Parallel shadow from " +str(ll)


def test4():
	'''point light shadows to multiple faces'''

	ground=App.ActiveDocument.Body005
	ufo=App.ActiveDocument.Body

	ll=App.Vector(-800,-0,800)
#	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[1],mode='Perspective',light=ll)
#	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[2],mode='Perspective',light=ll)

	rc=createShadow(ufo=ufo,ground=ground,mode='Perspective',light=ll)

	ll=App.Vector(800,-0,800)
#	rc=createShadow(ufo=ufo,ground=ground,mode='Perspective',light=ll)


def test4a():
	'''point light shadows to multiple faces'''

	ground=App.ActiveDocument.Body005
	ufo=App.ActiveDocument.Body

	ll=App.Vector(-800,-0,800)
	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[1],mode='Perspective',light=ll)


	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[2],mode='Perspective',light=ll)
	rc=createShadow(ufo=ufo,ground=ground,mode='Perspective',light=ll)

	ll=App.Vector(800,-0,800)
	rc=createShadow(ufo=ufo,ground=ground,mode='Perspective',light=ll)


def test5():
	''' dust shadow for parallel light '''

	ground=App.ActiveDocument.Body004
	ufo=App.ActiveDocument.Sketch004
	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[3,2],mode='Parallel',light=App.Vector(-1000,450,200))
	createShadowSpace4(rc)
	App.ActiveDocument.ActiveObject.Label="Dust Light of Window 1"
	delo(rc)

	ufo=App.ActiveDocument.Sketch005
	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[3,2],mode='Parallel',light=App.Vector(-1000,450,200))
	createShadowSpace4(rc)

	App.ActiveDocument.ActiveObject.Label="Dust Light of Window 2"
	delo(rc)


def test6():
	''' dust shadow for point light '''

	ground=App.ActiveDocument.Body004
	ufo=App.ActiveDocument.Sketch004
	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[3,2],mode='Perspective',light=App.Vector(-400,-2540,490))
	createShadowSpace5(rc)

	App.ActiveDocument.ActiveObject.Label="Dust Light of Window 1"
	showlab(App.ActiveDocument.ActiveObject.Label,offset=(0,0,10),color=(.7,1.0,0.7))
	delo(rc)

	ufo=App.ActiveDocument.Sketch005
	rc=createShadow(ufo=ufo,ground=ground,groundIndex=[3,2],mode='Perspective',light=App.Vector(-400,-2540,490))
	createShadowSpace5(rc)

	App.ActiveDocument.ActiveObject.Label="Dust Light of Window 2"
	showlab(App.ActiveDocument.ActiveObject.Label,offset=(0,0,10),color=(.7,1.0,0.7))
	delo(rc)

	showlab("House")
	showlab("Window1")
	showlab("Window21")


'''
test2()
test3()
test4()
test5()
test6()
'''



test6()
