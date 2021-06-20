'''
proctree.js
Copyright (c) 2012, Paul Brunt
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, self list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, self list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of tree.js nor the
      names of its contributors may be used to endorse or promote products
      derived from self software without specific prior written permission.

self SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL PAUL BRUNT BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES
LOSS OF USE, DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF self
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import math
import FreeCAD, Draft
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

    import Part
    import pivy
    from pivy import coin
    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "FreeCAD Fixed Rack"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")


def makeBuilding(objectslist=None, baseobj=None, name="Tree"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Building")
    _Building(obj)
    _ViewProviderBuilding(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj
'''
def gen_haus(le,wi,hiall,hi,ang,midx=0.7,wx=0.5,midy=0.5,wy=0):
	h=gen_haus0(le,wi,hiall,hi,midx,wx,midy,wy)
	Part.show(h)
	p=FreeCAD.ActiveDocument.ActiveObject
	p.Placement.Rotation.Angle=ang*math.pi/180
	return p
'''

class _Building(ArchComponent.Component):
    "A Shadow Tree Obcject"

    def __init__(self, obj):
        # Definición de  variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        self.obj = obj
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False


        # ESto son propiedades. Mover y convertir a propiedades
        self.clumpMax = 0.8
        self.clumpMin = 0.5
        self.lengthFalloffFactor = 0.85
        self.lengthFalloffPower = 1
        self.branchFactor = 2.0
        self.radiusFalloffRate = 0.6
        self.climbRate = 1.5
        self.trunkKink = 0.00
        self.maxRadius = 0.25
        self.treeSteps = 2
        self.taperRate = 0.95
        self.twistRate = 13
        self.segments = 6
        self.levels = 3
        self.sweepAmount = 0
        self.initalBranchLength = 0.85
        self.trunkLength = 2.5
        self.dropAmount = 0.0
        self.growAmount = 0.0
        self.vMultiplier = 0.2
        self.twigScale = 2.0
        self.seed = 10
        self.rseed = 10

        '''
        for i in data:
            if self.properties[i] != None:
                self.properties[i] = data[i]
        '''

        self.rseed = self.seed
        self.root = Branch([0, self.trunkLength, 0], self)
        self.root.length = self.initalBranchLength
        self.verts = []
        self.faces = []
        self.normals = []
        self.UV = []
        self.vertsTwig = []
        self.normalsTwig = []
        self.facesTwig = []
        self.uvsTwig = []
        #self.root.split(None, None, self.properties)
        self.createForks()
        self.createTwigs()
        self.doFaces()
        self.calcNormals()

    def random(self, a):
        if not a:
            a = self.rseed + 1
        return math.abs(math.cos(a + a * a))

    def setProperties(self, obj):
        # Definicion de Propiedades:
        ArchComponent.Component.setProperties(self, obj)

        # CANOPY: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "CanopyHeight",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).CanopyHeight = 4000

        obj.addProperty("App::PropertyLength",
                        "CanopyRadius",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).CanopyRadius = 1500

        obj.addProperty("App::PropertyFloat",
                        "Spikiness",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Spikiness = 0.15

        obj.addProperty("App::PropertyFloat",
                        "Lumpiness",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Lumpiness = 0.15

        obj.addProperty("App::PropertyFloat",
                        "Crown",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Crown = 1.0

        obj.addProperty("App::PropertyQuantity",
                        "LeafCount",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).LeafCount = 64

        # TRUNK: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "TrunkHeight",
                        "Trunk",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).TrunkHeight = 1122

        obj.addProperty("App::PropertyLength",
                        "TrunkRadius",
                        "Trunk",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).TrunkRadius = 147

        obj.addProperty("App::PropertyQuantity",
                       "TrunkFaces",
                       "Trunk",
                       QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                       ).TrunkFaces = 6

        obj.setEditorMode("TrunkFaces", 1)

        self.Type = "Fixed Rack"
        obj.Proxy = self

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def viereck(le, wi, he, inlea=0, inleb=0, inwia=0, inwib=0):
        '''gugu'''
        liste = [
            (0 + inlea, inwia, he),
            (le - inleb, inwia, he),
            (le - inleb, wi - inwib, he),
            (inlea, wi - inwib, he),
            (inlea, inwia, he)
        ]
        return liste

    def generateBuilding (le, wi, hiall, hi, midx, wx, midy, wy):

        he=hiall
        he3=hi

        inle=8
        inwi=2
        if wx==0: wx=0.0001
        if wy==0: wy=0.0001

        if midx<0.5:
            bix=le*midx
        else:
            bix=le*(1-midx)

        if midy<0.5:
            biy=wi*midy
        else:
            biy=wi*(1-midy)

        list1=viereck(le,wi,0)
        list2=viereck(le,wi,he)
        list3=viereck(le,wi,he3,
            le*midx-bix*wx,le-(le*midx+bix*wx),
            wi*midy-biy*wy,wi-(wi*midy+biy*wy),
        )

        poly1 = Part.makePolygon( list1)
        poly3 = Part.makePolygon( list3)
        face1 = Part.Face(poly1)
        face3 = Part.Face(poly3)
        faceListe=[face1,face3]

        for i in range(len(list1)-1):
            liste3=[list1[i],list1[i+1],list2[i+1],list2[i],list1[i]]
            poly=Part.makePolygon(liste3)
            face = Part.Face(poly)
            faceListe.append(face)

        for i in range(len(list2)-1):
            liste3=[list2[i],list2[i+1],list3[i+1],list3[i],list2[i]]
            poly=Part.makePolygon(liste3)
            face = Part.Face(poly)
            faceListe.append(face)

        myShell = Part.makeShell(faceListe)
        mySolid = Part.makeSolid(myShell)
        return mySolid



    def execute(self, obj):
        print("  -----  TREE  -  EXECUTE  ----------")
        from datetime import datetime
        starttime = datetime.now()

        pl = obj.Placement
            ## aquí el código ------------------------------


        obj.Placement = pl


        print("  --  Tree done: (", datetime.now() - starttime, ")")


class _ViewProviderTree(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "tree(1).svg"))


class _TrackerTaskPanel:

    def __init__(self, obj=None):
        self.obj = obj

        self.formRack = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

        # signals/slots
        # QtCore.QObject.connect(self.valueModuleLength,QtCore.SIGNAL("valueChanged(double)"),self.setModuleLength)
        # QtCore.QObject.connect(self.valueModuleWidth,QtCore.SIGNAL("valueChanged(double)"),self.setModuleWidth)
        # QtCore.QObject.connect(self.valueModuleHeight,QtCore.SIGNAL("valueChanged(double)"),self.setModuleHeight)
        # QtCore.QObject.connect(self.valueModuleFrame, QtCore.SIGNAL("valueChanged(double)"), self.setModuleFrame)
        # QtCore.QObject.connect(self.valueModuleColor, QtCore.SIGNAL("valueChanged(double)"), self.setModuleColor)
        # QtCore.QObject.connect(self.valueModuleGapX, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapX)
        # QtCore.QObject.connect(self.valueModuleGapY, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapY)

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


class _CommandBuild:
    "the PVPlant Tree command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "tree(1).svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTree", "Tree"),
                'Accel': "S, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTree",
                                                    "Creates a Tree object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        print("_CommandTracker - Activated")
        obj = makeTree()
        self.TreePanel = _TreeTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TreePanel)
        return


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantTree', _CommandBuild())