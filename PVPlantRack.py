# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Javier Braña <javier.branagutierrez@gmail.com>  *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************
import math

import FreeCAD
import ArchComponent
import PVPlantSite
import Part
import Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
    from pivy import coin

else:
    # \cond
    def translate(ctxt, txt):
        return txt

    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "PVPlant Frames"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import os
import PVPlantResources
from PVPlantResources import DirIcons as DirIcons

def selectFrames():
    objectlist = list()
    #FreeCAD.ActiveDocument.findObjects(Name="Tracker")
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, "Proxy") and obj.Proxy.isDerivedFrom("Frame"):
            objectlist.append(obj)
    return objectlist if len(objectlist) > 0 else None

def makeFrameSetup(name="FrameSetup"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    FrameSetup(obj)
    ViewProviderFrameSetup(obj.ViewObject)
    return obj

class FrameSetup:
    "A Base Frame Setup Class"
    def __init__(self, obj):
        # Definición de Variables:
        self.obj = obj

    def setProperties(self, obj):
        ''' Definición de Propiedades: '''
        pl = obj.PropertiesList
        # Modulo: ------------------------------------------------------------------------------------------------------
        if not "ModuleThick" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleThick",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleThick = 40

        if not "ModuleWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleWidth",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).ModuleWidth = 1130

        if not "ModuleHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleHeight",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).ModuleHeight = 2250

        if not "PoleCableLength" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleCableLength",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).PoleCableLength = 1200

        if not "ModulePower" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModulePower",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).ModulePower = 600

        # Array de modulos: -------------------------------------------------------------------------------------------
        if not "ModuleColumns" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModuleColumns",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleColumns = 2

        if not "ModuleRows" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModuleRows",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleRows = 2

        if not "ModuleColGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleColGap",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleColGap = 20

        if not "ModuleRowGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleRowGap",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleRowGap = 20

        if not "ModuleOffsetX" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleOffsetX",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleOffsetX = 0

        if not "ModuleOffsetY" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleOffsetY",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleOffsetY = 0

        if not "ModuleOrientation" in pl:
            obj.addProperty("App::PropertyEnumeration",
                            "ModuleOrientation",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleOrientation = ["Portrait", "Landscape"]

        if not "ModuleViews" in pl:
            obj.addProperty("App::PropertyBool",
                            "ModuleViews",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleViews = True

        # Frame --------------------------------------------------------------------------------------------------------
        '''if not "Tilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "Tilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).Tilt = 30'''

        if not "MaxLengthwiseTilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxLengthwiseTilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "Máxima inclinación longitudinal")
                            ).MaxLengthwiseTilt = 15

        if not "Width" in pl:
            obj.addProperty("App::PropertyDistance",
                            "Width",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "Largo de la estructura")
                            )
            obj.setEditorMode("Width", 1)

        if not "Length" in pl:
            obj.addProperty("App::PropertyDistance",
                            "Length",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "Ancho de la estructura")
                            )
            obj.setEditorMode("Length", 1)

        if not "TotalAreaShape" in pl:
            obj.addProperty("App::PropertyDistance",
                            "TotalAreaShape",
                            "Frame",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Total Area de los Paneles")
                            )
            obj.setEditorMode("TotalAreaShape", 1)

    def onChanged(self, obj, prop):
        '''  '''

class Frame(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setProperties(obj)

        # Does a IfcType exist?
        obj.IfcType = "Structural Item"
        obj.setEditorMode("IfcType", 1)

        self.totalAreaShape = None
        self.changed = True

    def setProperties(self, obj):
        # Definicion de Propiedades:
        print("Frame - setProperties")
        ArchComponent.Component.setProperties(self, obj)

        pl = obj.PropertiesList
        # Modulo: ------------------------------------------------------------------------------------------------------
        if not "ModuleThick" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleThick",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleThick = 40
        if not "ModuleWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleWidth",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).ModuleWidth = 992
        if not "ModuleHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "ModuleHeight",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).ModuleHeight = 1996
        if not "PoleCableLength" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleCableLength",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).PoleCableLength = 1200
        if not "ModulePower" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModulePower",
                            "Module",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).ModulePower = 400

        # Array de modulos: -------------------------------------------------------------------------------------------
        if not "ModuleCols" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModuleCols",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleCols = 15

        if not "ModuleRows" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "ModuleRows",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleRows = 2

        if not "ModuleColGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleColGap",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleColGap = 20

        if not "ModuleRowGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleRowGap",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleRowGap = 20

        if not "ModuleOffsetX" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleOffsetX",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleOffsetX = 0

        if not "ModuleOffsetY" in pl:
            obj.addProperty("App::PropertyDistance",
                            "ModuleOffsetY",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ModuleOffsetY = 0

        if not "ModuleOrientation" in pl:
            obj.addProperty("App::PropertyEnumeration",
                            "ModuleOrientation",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleOrientation = ["Portrait", "Landscape"]

        if not "ModuleViews" in pl:
            obj.addProperty("App::PropertyBool",
                            "ModuleViews",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleViews = True
        '''
        if not "Modules" in pl:
            obj.addProperty("App::PropertyLinkSubListChild",
                            "Modules",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleViews = True
        '''

        # Frame --------------------------------------------------------------------------------------------------------
        if not "Tilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "Tilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).Tilt = 30

        if not "MaxLengthwiseTilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxLengthwiseTilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "Máxima inclinación longitudinal")
                            ).MaxLengthwiseTilt = 15

        # Frame outputs -----------------------------
        if not "Width" in pl:
            obj.addProperty("App::PropertyDistance",
                            "Width",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "Ancho de la estructura")
                            )
        obj.setEditorMode("Width", 1)

        if not "Length" in pl:
            obj.addProperty("App::PropertyDistance",
                            "Length",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "Largo de la estructura")
                            )
        obj.setEditorMode("Length", 1)

        if not "TotalArea" in pl:
            obj.addProperty("App::PropertyArea",
                            "TotalArea",
                            "Frame",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Area total de los Paneles")
                            )
        obj.setEditorMode("TotalArea", 1)


        # Neighbours:

        if not "North" in pl:
            obj.addProperty("App::PropertyLink",
                            "North",
                            "Neighbours",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Area total de los Paneles")
                            )

        if not "South" in pl:
            obj.addProperty("App::PropertyLink",
                            "South",
                            "Neighbours",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Area total de los Paneles")
                            )

        if not "East" in pl:
            obj.addProperty("App::PropertyLink",
                            "East",
                            "Neighbours",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Area total de los Paneles")
                            )

        if not "West" in pl:
            obj.addProperty("App::PropertyLink",
                            "West",
                            "Neighbours",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Area total de los Paneles")
                            )



        '''# Placement
        if not "Route" in pl:
            obj.addProperty("App::PropertyLink",
                            "Route",
                            "Placement",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Total Area de los Paneles")
                            )
        obj.setEditorMode("Route", 1)

        if not "RouteSection" in pl:
            obj.addProperty("App::PropertyIntegerConstraint",
                            "RouteSection",
                            "Placement",
                            QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                              "Total Area de los Paneles")
                            )
        obj.setEditorMode("RouteSection", 1)'''

        self.Type = "Frame"

    def onChanged(self, obj, prop):
        if prop == "North":
            if obj.getPropertyByName(prop):
                obj.getPropertyByName("Route").South = obj

        if (prop == "Route"):
            if obj.getPropertyByName(prop):
                obj.RouteSection = (1, 1, len(obj.getPropertyByName("Route").Shape.Edges) + 1, 1)

    def getTotalAreaShape(self):
        return self.totalAreaShape


''' ------------------------------------------- Fixed Structure --------------------------------------------------- '''


def makeRack(name="Rack"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _FixedRack(obj)
    _ViewProviderFixedRack(obj.ViewObject)
    # FreeCAD.ActiveDocument.recompute()
    return obj


class _FixedRack(Frame):
    "A Fixed Rack Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        Frame.__init__(self, obj)
        Frame.setProperties(self, obj)
        self.setProperties(obj)
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False

    def setProperties(self, obj):
        pl = obj.PropertiesList

        # Array of Posts: ------------------------------------------------------------------------------------------------------
        if not "NumberPostsX" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "NumberPostsX",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).NumberPostsX = 5

        if not "DistancePostsX" in pl:
            obj.addProperty("App::PropertyLength",
                            "DistancePostsX",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).DistancePostsX = 3000

        if not "FrontPost" in pl:
            obj.addProperty("App::PropertyBool",
                            "FrontPost",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).FrontPost = False

        if not "DistancePostsY" in pl:
            obj.addProperty("App::PropertyLength",
                            "DistancePostsY",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).DistancePostsY = 2000

        if not "RammingDeep" in pl:
            obj.addProperty("App::PropertyLength",
                            "RammingDeep",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).RammingDeep = 1500
        # Correas: ----------------------------------------------------------------------------------------------------
        if not "BeamHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamHeight",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamHeight = 80

        if not "BeamWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamWidth",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).BeamWidth = 50

        if not "BeamOffset" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamOffset",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamOffset = 50

        if not "BeamSpacing" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamSpacing",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamSpacing = 1000

        self.Type = "Fixed Rack"

    def onDocumentRestored(self, obj):
        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    '''
    def addObject(self, child):
        print("addObject")

    def removeObject(self, child):
        print("removeObject")

    def onChanged(self, obj, prop):
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
    '''

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        # FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def CalculateModuleArray(self, obj, totalh, totalw, moduleh, modulew):
        # ModuleThick
        # ModuleWidth
        # ModuleThinness
        # ModuleColor
        # ModuleCols
        # ModuleRows
        # ModuleColGap
        # ModuleRowGap

        # BeamHeight
        # BeamWidth
        # BeamOffset

        import Part, Draft

        # pl = obj.Placement
        module = Part.makeBox(modulew, moduleh, obj.ModuleThick.Value)
        correa = Part.makeBox(totalw + obj.BeamOffset.Value * 2, obj.BeamWidth.Value, obj.BeamHeight.Value)

        # Longitud poste - Produndidad de hincado + correas
        correaoffsetz = obj.BackPostLength.Value
        offsetz = correaoffsetz + obj.BeamHeight.Value

        p1 = FreeCAD.Vector(0, 0, 0)
        p2 = FreeCAD.Vector(totalw, 0, 0)
        p3 = FreeCAD.Vector(totalw, totalh, 0)
        p4 = FreeCAD.Vector(0, totalh, 0)
        totalArea = Part.Face(Part.makePolygon([p1, p2, p3, p4, p1]))

        totalArea = Part.makePlane(totalw, totalh)
        totalArea.Placement.Base.x = -totalw / 2
        totalArea.Placement.Base.y = -totalh / 2
        totalArea.Placement.Base.z = obj.BeamHeight.Value

        self.ModuleArea = totalArea
        # if ShowtotalArea:
        self.ListModules.append(totalArea)

        correaoffsety = (moduleh - obj.BeamSpacing.Value - obj.BeamWidth.Value) / 2
        for y in range(int(obj.ModuleRows.Value)):
            for x in range(int(obj.ModuleCols.Value)):
                xx = totalArea.Placement.Base.x + (modulew + obj.ModuleColGap.Value) * x
                yy = totalArea.Placement.Base.y + (moduleh + obj.ModuleRowGap.Value) * y
                zz = obj.BeamHeight.Value
                moduleCopy = module.copy()
                moduleCopy.Placement.Base.x = xx
                moduleCopy.Placement.Base.y = yy
                moduleCopy.Placement.Base.z = zz
                self.ListModules.append(moduleCopy)

        compound = Part.makeCompound(self.ListModules)
        compound.Placement.Base.z = correaoffsetz - obj.RammingDeep.Value

        if obj.FrontPost:
            base = FreeCAD.Vector(0, (-obj.BackPostHeight.Value + obj.DistancePostsY.Value) / 2,
                                  correaoffsetz - obj.RammingDeep.Value)
        else:
            base = FreeCAD.Vector(0, -obj.BackPostHeight.Value / 2 + totalh / 3,
                                  correaoffsetz - obj.RammingDeep.Value)

        a = compound.rotate(base, FreeCAD.Vector(1, 0, 0), obj.Tilt)

        del correa
        del module
        del compound
        del self.ListModules[:]

        self.ListModules.append(a)

    def CalculatePosts(self, obj, totalh, totalw):
        '''
        # NumberPostsX
        # NumberPostsY
        # PostHeight
        # PostWidth
        # PostLength
        # DistancePostsX
        # DistancePostsY
        '''

        postBack = Part.makeBox(obj.BackPostWidth.Value, obj.BackPostHeight.Value, obj.BackPostLength.Value)
        postFront = Part.makeBox(obj.FrontPostWidth.Value, obj.FrontPostHeight.Value, obj.FrontPostLength.Value)

        angle = obj.Placement.Rotation.toEuler()[1]
        offsetX = (-obj.DistancePostsX.Value * (obj.NumberPostsX.Value - 1)) / 2

        # offsetY = (-obj.PostHeight.Value - obj.DistancePostsY * (obj.NumberPostsY - 1)) / 2
        if obj.FrontPost:
            offsetY = (-obj.BackPostHeight.Value + obj.DistancePostsY.Value) / 2
        else:
            # TODO: cambiar el totalh / 3 por el valor adecuado
            offsetY = -obj.BackPostHeight.Value / 2 + totalh / 3

        offsetZ = -obj.RammingDeep.Value

        for x in range(int(obj.NumberPostsX.Value)):
            xx = offsetX + (
                    obj.NumberPostsX.Value + obj.DistancePostsX.Value) * x  # * math.cos(obj.Placement.Rotation.toEuler()[1])
            yy = offsetY
            zz = offsetZ  # * math.sin(obj.Placement.Rotation.toEuler()[1])

            postCopy = postBack.copy()
            postCopy.Placement.Base.x = xx
            postCopy.Placement.Base.y = yy
            postCopy.Placement.Base.z = zz
            base = FreeCAD.Vector(xx, yy, obj.BackPostHeight.Value - offsetZ)
            postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
            self.ListPosts.append(postCopy)

            if obj.FrontPost:
                postCopy = postFront.copy()
                postCopy.Placement.Base.x = xx
                postCopy.Placement.Base.y = -yy
                postCopy.Placement.Base.z = zz
                base = FreeCAD.Vector(xx, yy, obj.FrontPostHeight.Value - offsetZ)
                postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
                self.ListPosts.append(postCopy)

        del postBack
        del postFront

    def execute(self, obj):

        pl = obj.Placement

        del self.ListModules[:]
        del self.ListPosts[:]

        self.ListModules = []
        self.ListPosts = []

        if obj.ModuleOrientation == "Portrait":
            w = obj.ModuleWidth.Value
            h = obj.ModuleHeight.Value
        else:
            h = obj.ModuleWidth.Value
            w = obj.ModuleHeight.Value

        totalh = h * obj.ModuleRows + obj.ModuleRowGap.Value * (obj.ModuleRows - 1)
        totalw = w * obj.ModuleCols + obj.ModuleColGap.Value * (obj.ModuleCols - 1)
        obj.Width = totalw
        obj.Length = totalh

        # hacer el shape:
        self.CalculateModuleArray(obj, totalh, totalw, h, w)
        self.CalculatePosts(obj, totalh, totalw)

        allShapes = []
        allShapes.extend(self.ListModules)
        allShapes.extend(self.ListPosts)
        compound = Part.makeCompound(allShapes)
        obj.Shape = compound
        obj.Placement = pl

        angle = obj.Placement.Rotation.toEuler()[1]
        if angle > obj.MaxLengthwiseTilt:
            obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
        print("fin")


class _ViewProviderFixedRack(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)
        '''
        ArchSite._ViewProviderSite.__init__(self, vobj)
        vobj.Proxy = self
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        self.setProperties(vobj)
        '''

    def getIcon(self):
        """ Return the path to the appropriate icon. """
        return str(os.path.join(DirIcons, "solar-fixed.svg"))

    def setEdit(self, vobj, mode):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard Arch component task panel.

        Parameters
        ----------
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].

        Returns
        -------
        bool
            If edit mode was entered.
        """

        if (mode == 0) and hasattr(self, "Object"):
            taskd = _FixedRackTaskPanel(self.Object)
            taskd.obj = self.Object
            FreeCADGui.Control.showDialog(taskd)
            return True
        return False

class _FixedRackTaskPanel:
    def __init__(self, obj=None):
        self.obj = obj

        # -------------------------------------------------------------------------------------------------------------
        # Module widget form
        # -------------------------------------------------------------------------------------------------------------
        self.formRack = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


''' ------------------------------------------- Tracker Structure --------------------------------------------------- '''
def makeTrackerSetup(name="TrackerSetup"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "TrackerSetup")
    obj.Label = name
    TrackerSetup(obj)
    ViewProviderTrackerSetup(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    try:
        site = PVPlantSite.get()
        frame_list = site.Frames
        frame_list.append(obj)
        site.Frames = frame_list
    except:
        pass
    return obj

class TrackerSetup(FrameSetup):
    "A 1 Axis Tracker Obcject"

    def __init__(self, obj):
        FrameSetup.__init__(self, obj)
        self.setProperties(obj)
        obj.ModuleColumns = 45
        obj.ModuleRows = 2
        obj.ModuleColGap = 20
        obj.ModuleRowGap = 20
        #obj.Tilt = 0

    def setProperties(self, obj):
        FrameSetup.setProperties(self, obj)
        pl = obj.PropertiesList

        # Array de modulos: -------------------------------------------------------------------------------------------
        if not "MotorGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "MotorGap",
                            "ModuleArray",
                            QT_TRANSLATE_NOOP("App::Property", "Thse height of this object")
                            ).MotorGap = 550

        if not "UseGroupsOfModules" in pl:
            obj.addProperty("App::PropertyBool",
                            "UseGroupsOfModules",
                            "GroupsOfModules",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).UseGroupsOfModules = False

        # Poles: ------------------------------------------------------------------------------------------------------
        #TODO: cambiar todo esto por una lista de objetos??
        if not "PoleHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleHeight",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).PoleHeight = 160

        if not "PoleWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleWidth",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).PoleWidth = 80

        if not "PoleLength" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleLength",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).PoleLength = 3000

        # Array of Posts: ------------------------------------------------------------------------------------------------------
        if not "NumberPole" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "NumberPole",
                            "Poles",
                            "The total number of poles"
                            ).NumberPole = 7

        if not "DistancePole" in pl:
            obj.addProperty("App::PropertyIntegerList",  # No list of Lenght so I use float list
                            "DistancePole",
                            "Poles",
                            "Distance between poles starting from the left and from the first photovoltaic module "
                            "without taking into account the offsets"
                            ).DistancePole = [7000, 7000, 7000, 7000, 7000, 7000, 7000]

        if not "AerialPole" in pl:
            obj.addProperty("App::PropertyIntegerList",
                            "AerialPole",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).AerialPole = [1050]

        if not "Poles" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "Poles",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        # Correas: ----------------------------------------------------------------------------------------------------
        # 1. MainBeam: -------------------------------------------------------------------------------------------------
        if not "MainBeamHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamHeight",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamHeight = 120

        if not "MainBeamWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamWidth",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamWidth = 120

        if not "MainBeamAxisPosition" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamAxisPosition",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamAxisPosition = 1278
        # 2. Costillas: ----------------------------------------------------------------------------------------------------
        if not "ShowBeams" in pl:
            obj.addProperty("App::PropertyBool",
                            "ShowBeams",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ShowBeams = False

        if not "BeamHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamHeight",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamHeight = 80

        if not "BeamWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamWidth",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).BeamWidth = 83.2

        if not "BeamOffset" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamOffset",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamOffset = 50

        if not "BeamSpacing" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamSpacing",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamSpacing = 1000

        # Tracker --------------------------------------------------------------------------------------------------------
        if not "MaxPhi" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxPhi",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MaxPhi = 60

        if not "MinPhi" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MinPhi",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MinPhi = -60

        if not "MaxNegativeLengthwiseTilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxNegativeLengthwiseTilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MaxNegativeLengthwiseTilt = 6

        self.Type = "1 Axis Tracker"
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''
        FrameSetup.onChanged(self, obj, prop)
        '''
        ['Additions', 'AerialPole', 'Axis', 'Base', 'BeamHeight', 'BeamOffset', 'BeamSpacing', 'BeamWidth', 'CloneOf',
        'Description', 'DistancePole', 'ExpressionEngine', 'HiRes', 'HorizontalArea', 'IfcData', 'IfcProperties', 
        'IfcType', 'Label', 'Label2', 'Length', 'MainBeamAxisPosition', 'MainBeamHeight', 'MainBeamWidth', 'Material', 
        'MaxLengthwiseTilt', 'MaxNegativeLengthwiseTilt', 'MaxPhi', 'MinPhi', 'ModuleColGap', 'ModuleCols', 
        'ModuleHeight', 'ModuleOffsetX', 'ModuleOffsetY', 'ModuleOrientation', 'ModulePower', 'ModuleRowGap', 
        'ModuleRows', 'ModuleThick', 'ModuleViews', 'ModuleWidth', 'MotorGap', 'MoveBase', 'MoveWithHost', 'NumberPole', 
        'PerimeterLength', 'Placement', 'PoleCableLength', 'PoleHeight', 'PoleLength', 'PoleWidth', 'Proxy', 'Route', 
        'RouteSection', 'Shape', 'ShowBeams', 'StandardCode', 'Subtractions', 'Tag', 'Tilt', 'TotalAreaShape', 
        'UseGroupsOfModules', 'VerticalArea', 'Visibility', 'Width']
        '''

        if prop == "UseGroupsOfModules":
            if obj.getPropertyByName(prop) == True:
                if not "ColumnsPerGroup" in obj.PropertiesList:
                    obj.addProperty("App::PropertyIntegerList",
                                    "ColumnsPerGroup",
                                    "GroupsOfModules",
                                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                                    )

                if not "GroupGaps" in obj.PropertiesList:
                    obj.addProperty("App::PropertyIntegerList",
                                    "GroupGaps",
                                    "GroupsOfModules",
                                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                                    )

            else:
                if "ColumnsPerGroup" in obj.PropertiesList:
                    obj.removeProperty("ColumnsPerGroup")
                if "GroupGaps" in obj.PropertiesList:
                    obj.removeProperty("GroupGaps")

    def CalculateModuleArray(self, obj, totalh, totalw, moduleh, modulew):
        module = Part.makeBox(modulew, moduleh, obj.ModuleThick.Value)
        compound = Part.makeCompound([])
        offsetx = -totalw / 2
        offsety = -totalh / 2
        offsetz = obj.MainBeamHeight.Value + obj.BeamHeight.Value

        if obj.ModuleViews:
            mid = int(obj.ModuleColumns.Value / 2)
            for row in range(int(obj.ModuleRows.Value)):
                for col in range(int(obj.ModuleColumns.Value)):
                    xx = offsetx + (modulew + obj.ModuleColGap.Value) * col
                    if col >= mid:
                        xx += obj.MotorGap.Value - obj.ModuleColGap.Value
                    yy = offsety + (moduleh + obj.ModuleRowGap.Value) * row
                    zz = offsetz
                    moduleCopy = module.copy()
                    moduleCopy.Placement.Base = FreeCAD.Vector(xx, yy, zz)
                    compound.add(moduleCopy)
        else:
            totalArea = Part.makePlane(totalw, totalh)
            totalArea.Placement.Base = FreeCAD.Vector(offsetx, offsety, offsetz)
            compound.add(totalArea)
        return compound

    def calculateBeams(self, obj, totalh, totalw, moduleh, modulew):
        ''' make mainbeam and modules beams '''
        compound = Part.makeCompound([])
        mainbeam = Part.makeBox(totalw + obj.ModuleOffsetX.Value * 2,
                                obj.MainBeamWidth.Value,
                                obj.MainBeamHeight.Value)
        # details --------------------------------------------------------------------------------------------
        '''
        edg = []
        max_length = max([edge.Length for edge in mainbeam.Edges])
        for edge in mainbeam.Edges:
            if edge.Length == max_length:
                edg.append(edge)
        mainbeam = mainbeam.makeFillet(6, edg)
        tmp = Part.makeBox((totalw + obj.ModuleOffsetX.Value * 2) * 2, obj.MainBeamWidth.Value, obj.MainBeamHeight.Value)
        tmp.Placement.Base.x -= tmp.BoundBox.XLength / 4
        edg = []
        max_length = max([edge.Length for edge in tmp.Edges])
        for edge in tmp.Edges:
            if edge.Length == max_length:
                edg.append(edge)
        tmp = tmp.makeFillet(6, edg)
        tmp = tmp.makeOffsetShape(-3, 0.1)
        mainbeam = mainbeam.cut(tmp)
        '''
        # end details ----------------------------------------------------------------------------------------
        mainbeam.Placement.Base.x = -totalw / 2 - obj.ModuleOffsetX.Value
        mainbeam.Placement.Base.y = -obj.MainBeamWidth.Value / 2
        compound.add(mainbeam)

        # Correa profile:
        if obj.ShowBeams:  # TODO: make it in another function
            mid = int(obj.ModuleColumns.Value / 2)

            up = 27.8  # todo
            thi = 3.2  # todo

            p1 = FreeCAD.Vector(obj.BeamWidth.Value / 2 - up, 0, thi)
            p2 = FreeCAD.Vector(p1.x, 0, obj.BeamHeight.Value)
            p3 = FreeCAD.Vector(obj.BeamWidth.Value / 2, 0, p2.z)
            p4 = FreeCAD.Vector(p3.x, 0, obj.BeamHeight.Value - thi)
            p5 = FreeCAD.Vector(p4.x - up + thi, 0, p4.z)
            p6 = FreeCAD.Vector(p5.x, 0, 0)

            p7 = FreeCAD.Vector(-p6.x, 0, p6.z)
            p8 = FreeCAD.Vector(-p5.x, 0, p5.z)
            p9 = FreeCAD.Vector(-p4.x, 0, p4.z)
            p10 = FreeCAD.Vector(-p3.x, 0, p3.z)
            p11 = FreeCAD.Vector(-p2.x, 0, p2.z)
            p12 = FreeCAD.Vector(-p1.x, 0, p1.z)

            p = Part.makePolygon([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p1])
            p = Part.Face(p)
            profile = p.extrude(FreeCAD.Vector(0, 428, 0))

            for col in range(int(obj.ModuleColumns.Value)):
                xx = totalArea.Placement.Base.x + (modulew + obj.ModuleColGap.Value) * col
                if col >= mid:
                    xx += float(obj.MotorGap.Value) - obj.ModuleColGap.Value
                correaCopy = profile.copy()
                correaCopy.Placement.Base.x = xx
                correaCopy.Placement.Base.y = -428 / 2
                correaCopy.Placement.Base.z = obj.MainBeamHeight.Value
                self.ListModules.append(correaCopy)
                compound.add(correaCopy)

        return compound

    def CalculatePosts(self, obj, totalh, totalw):
        def getarray(array, numberofpoles):
            if len(array) == 0:
                newarray = [0] * numberofpoles
                return newarray
            elif len(array) == 1:
                newarray = [array[0]] * numberofpoles
                return newarray
            elif len(array) == 2:
                newarray = [array[0]] * numberofpoles
                half = int(numberofpoles / 2)
                newarray[half] = array[1]
                if numberofpoles % 2 == 0:
                    newarray[half - 1] = array[1]
                return newarray
            elif len(array) == 3:
                half = int(numberofpoles/2)
                newarray = [array[0]] * half + [array[1]] + [array[2]] * half
                if numberofpoles % 2 == 0:
                    newarray[half] = array[1]
                return newarray
            elif len(array) == numberofpoles:
                return array
            elif len(array) > numberofpoles:
                return array[0 : numberofpoles]
            else:
                newarray = [array[0]] * numberofpoles
                return newarray

        #TODO: cambiar posttmp
        posttmp = Part.makeBox(obj.PoleWidth.Value, obj.PoleHeight.Value, obj.PoleLength.Value)
        linetmp = Part.LineSegment(FreeCAD.Vector(0), FreeCAD.Vector(0, obj.PoleHeight.Value / 2, 0)).toShape()
        compoundPoles = Part.makeCompound([])
        compoundAxis = Part.makeCompound([])

        offsetX = - totalw / 2
        offsetY = -obj.PoleHeight.Value / 2
        arrayDistance = getarray(obj.DistancePole, int(obj.NumberPole.Value))
        arrayAerial = getarray(obj.AerialPole, int(obj.NumberPole.Value))

        for x in range(int(obj.NumberPole.Value)):
            offsetX += arrayDistance[x] - obj.PoleWidth.Value / 2
            postCopy = posttmp.copy()
            postCopy.Placement.Base = FreeCAD.Vector(offsetX, offsetY, -(obj.PoleLength.Value - arrayAerial[x]))
            compoundPoles.add(postCopy)
            axis = linetmp.copy()
            axis.Placement.Base = FreeCAD.Vector(offsetX + obj.PoleWidth.Value / 2, offsetY, arrayAerial[x])
            compoundAxis.add(axis)

        return compoundPoles, compoundAxis

    def execute(self, obj):
        # obj.Shape: compound
        # |- Modules and Beams: compound
        # |-- Modules array: compound
        # |--- Modules: solid
        # |-- Beams: compound
        # |--- MainBeam: solid
        # |--- Secundary Beams: solid (if exist)
        # |- Poles array: compound
        # |-- Poles: solid
        # |-- Axis: Edge/line (if exist)

        if obj.ModuleOrientation == "Portrait":
            w = obj.ModuleWidth.Value
            h = obj.ModuleHeight.Value
        else:
            h = obj.ModuleWidth.Value
            w = obj.ModuleHeight.Value

        totalh = h * obj.ModuleRows + obj.ModuleRowGap.Value * (obj.ModuleRows - 1)
        totalw = w * obj.ModuleColumns + obj.ModuleColGap.Value * (obj.ModuleColumns - 1) + \
                 (obj.MotorGap.Value - obj.ModuleColGap.Value) if obj.MotorGap.Value > 0 else 0

        modules = self.CalculateModuleArray(obj, totalh, totalw, h, w)
        beams = self.calculateBeams(obj, totalh, totalw, h, w)
        poles, poleaxis = self.CalculatePosts(obj, totalh, totalw)
        compound = Part.makeCompound([modules, beams])
        compound.Placement.Base.z = obj.MainBeamAxisPosition.Value - (obj.MainBeamHeight.Value / 2)
        obj.Shape = Part.makeCompound([compound, Part.makeCompound([poles, poleaxis])])
        obj.Width = min(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)
        obj.Length = max(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)

class ViewProviderTrackerSetup:
    "A View Provider for the TrackerSetup object"

    def __init__(self, obj):
        '''Set this object to the proxy object of the actual view provider'''
        obj.Proxy = self

    def getIcon(self):
        return str(os.path.join(DirIcons, "trackersetup.svg"))

    def setEdit(self, vobj, mode):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard FRAME SETUP task panel.

        Parameters
        ----------
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].

        Returns
        -------
        bool
            If edit mode was entered.
        """

        if (mode == 0) and hasattr(self, "Object"):
            taskd = _TrackerTaskPanel(self.Object)
            taskd.obj = self.Object
            FreeCADGui.Control.showDialog(taskd)
            return True
        return False

def makeTracker(name = "Tracker", setup = None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Tracker")
    obj.Label = name
    Tracker(obj)
    _ViewProviderTracker(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    if setup is not None:
        obj.Setup = setup
    try:
        site = PVPlantSite.get()
        frame_list = site.Frames
        frame_list.append(obj)
        site.Frames = frame_list
    except:
        pass
    return obj

class Tracker(ArchComponent.Component):
    "A 1 Axis Tracker Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)

    def setProperties(self, obj):
        pl = obj.PropertiesList

        if not "Setup" in pl:
            obj.addProperty("App::PropertyLink",
                            "Setup",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        if not "Tilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "Tilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).Tilt = 0

        self.Type = "1 Axis Tracker"
        obj.Proxy = self
        self.oldTilt = 0

    def onDocumentRestored(self, obj):
        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def onBeforeChange(self, obj, prop):
        ''' '''

        if prop == "Tilt":
            self.oldTilt = obj.Tilt

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

        if prop == "Setup":
            if obj.Setup is None:
                obj.Shape = Part.Shape() #TODO: ver si se puede borrar el contenido del shape
            else:
                pl = obj.Placement
                obj.Shape = obj.Setup.Shape.copy()
                obj.Placement = pl

        '''if prop == "Placement":
            angle = obj.Placement.Rotation.toEuler()[1]
            newpoles = Part.makeCompound([])
            for i in range(len(obj.Shape.SubShapes[1].SubShapes[0].SubShapes)):
                pole = obj.Shape.SubShapes[1].SubShapes[0].SubShapes[i]
                axis = obj.Shape.SubShapes[1].SubShapes[1].SubShapes[i]
                base = axis.Vertexes[0].Point
                vec = axis.Vertexes[1].Point - axis.Vertexes[0].Point
                newpoles.add(pole.rotate(base, vec, -angle))
            poles = Part.makeCompound([newpoles, obj.Shape.SubShapes[1].SubShapes[1].copy()])
            obj.Shape = Part.makeCompound([obj.Shape.SubShapes[0].copy(), poles])'''

        if prop == "Tilt":
            shape = obj.Shape.copy()
            p1 = shape.SubShapes[0].SubShapes[1].SubShapes[0].CenterOfMass
            p2 = min(shape.SubShapes[0].SubShapes[1].SubShapes[0].Faces, key=lambda face: face.Area).CenterOfMass
            axis = p1 - p2
            face = max(obj.Shape.SubShapes[0].SubShapes[0].SubShapes[0].Faces, key=lambda face: face.Area)
            g = face.CenterOfMass
            normal = face.normalAt(*face.Surface.parameter(g))
            radian = normal.getAngle(FreeCAD.Vector(0, 0, 1))
            print(normal, " - ", math.degrees(radian))
            obj.Shape = Part.makeCompound([shape.SubShapes[0].rotate(p1, axis, obj.Tilt.Value), shape.SubShapes[1]])
    def execute(self, obj):
        # obj.Shape: compound
        # |- Modules and Beams: compound
        # |-- Modules array: compound
        # |--- Modules: solid
        # |-- Beams: compound
        # |--- MainBeam: solid
        # |--- Secundary Beams: solid (if exist)
        # |- Poles array: compound
        # |-- Poles: solid
        # |-- PoleAxes: Edge


        '''if obj.Setup is None:
            return

        pl = obj.Placement
        obj.Shape = obj.Setup.Shape.copy()
        obj.Placement = pl'''

        #obj.Width = min(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)
        #obj.Length = max(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)

class _Tracker(Frame): #old
    "A 1 Axis Tracker Obcject"

    def __init__(self, obj):
        Frame.__init__(self, obj)

        obj.ModuleCols = 45
        obj.ModuleRows = 2
        obj.ModuleColGap = 20
        obj.ModuleRowGap = 20
        obj.Tilt = 0

    def setProperties(self, obj):
        print("Tracker - setProperties")
        Frame.setProperties(self, obj)
        pl = obj.PropertiesList

        # Array de modulos: -------------------------------------------------------------------------------------------
        if not "MotorGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "MotorGap",
                            "Module_array",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MotorGap = 550

        if not "UseGroupsOfModules" in pl:
            obj.addProperty("App::PropertyBool",
                            "UseGroupsOfModules",
                            "GroupsOfModules",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).UseGroupsOfModules = False

        # Poles: ------------------------------------------------------------------------------------------------------
        #TODO: cambiar todo esto por una lista de objetos??
        if not "PoleHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleHeight",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).PoleHeight = 160

        if not "PoleWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleWidth",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).PoleWidth = 80

        if not "PoleLength" in pl:
            obj.addProperty("App::PropertyLength",
                            "PoleLength",
                            "Pole",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).PoleLength = 3000

        # Array of Posts: ------------------------------------------------------------------------------------------------------
        if not "NumberPole" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "NumberPole",
                            "Poles",
                            "The total number of poles"
                            ).NumberPole = 7

        if not "DistancePole" in pl:
            obj.addProperty("App::PropertyIntegerList",  # No list of Lenght so I use float list
                            "DistancePole",
                            "Poles",
                            "Distance between poles starting from the left and from the first photovoltaic module "
                            "without taking into account the offsets"
                            ).DistancePole = [1500, 3000, 7000, 7000, 7000, 7000, 7000]

        if not "AerialPole" in pl:
            obj.addProperty("App::PropertyIntegerList",
                            "AerialPole",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).AerialPole = [1050]

        if not "Poles" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "Poles",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        # Correas: ----------------------------------------------------------------------------------------------------
        # 1. MainBeam: -------------------------------------------------------------------------------------------------
        if not "MainBeamHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamHeight",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamHeight = 120

        if not "MainBeamWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamWidth",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamWidth = 120

        if not "MainBeamAxisPosition" in pl:
            obj.addProperty("App::PropertyLength",
                            "MainBeamAxisPosition",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MainBeamAxisPosition = 1278
        # 2. Costillas: ----------------------------------------------------------------------------------------------------
        if not "ShowBeams" in pl:
            obj.addProperty("App::PropertyBool",
                            "ShowBeams",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ShowBeams = False

        if not "BeamHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamHeight",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamHeight = 80

        if not "BeamWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamWidth",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).BeamWidth = 83.2

        if not "BeamOffset" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamOffset",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamOffset = 50

        if not "BeamSpacing" in pl:
            obj.addProperty("App::PropertyLength",
                            "BeamSpacing",
                            "Beam",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).BeamSpacing = 1000

        # Tracker --------------------------------------------------------------------------------------------------------
        if not "MaxPhi" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxPhi",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MaxPhi = 60

        if not "MinPhi" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MinPhi",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MinPhi = -60

        if not "MaxNegativeLengthwiseTilt" in pl:
            obj.addProperty("App::PropertyAngle",
                            "MaxNegativeLengthwiseTilt",
                            "Frame",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MaxNegativeLengthwiseTilt = 6

        self.Type = "1 Axis Tracker"
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

        Frame.onChanged(self, obj, prop)

        '''
        ['Additions', 'AerialPole', 'Axis', 'Base', 'BeamHeight', 'BeamOffset', 'BeamSpacing', 'BeamWidth', 'CloneOf',
        'Description', 'DistancePole', 'ExpressionEngine', 'HiRes', 'HorizontalArea', 'IfcData', 'IfcProperties', 
        'IfcType', 'Label', 'Label2', 'Length', 'MainBeamAxisPosition', 'MainBeamHeight', 'MainBeamWidth', 'Material', 
        'MaxLengthwiseTilt', 'MaxNegativeLengthwiseTilt', 'MaxPhi', 'MinPhi', 'ModuleColGap', 'ModuleCols', 
        'ModuleHeight', 'ModuleOffsetX', 'ModuleOffsetY', 'ModuleOrientation', 'ModulePower', 'ModuleRowGap', 
        'ModuleRows', 'ModuleThick', 'ModuleViews', 'ModuleWidth', 'MotorGap', 'MoveBase', 'MoveWithHost', 'NumberPole', 
        'PerimeterLength', 'Placement', 'PoleCableLength', 'PoleHeight', 'PoleLength', 'PoleWidth', 'Proxy', 'Route', 
        'RouteSection', 'Shape', 'ShowBeams', 'StandardCode', 'Subtractions', 'Tag', 'Tilt', 'TotalAreaShape', 
        'UseGroupsOfModules', 'VerticalArea', 'Visibility', 'Width']
        '''

        if prop == "UseGroupsOfModules":
            if obj.getPropertyByName(prop) == True:
                if not "ColumnsPerGroup" in obj.PropertiesList:
                    obj.addProperty("App::PropertyIntegerList",
                                    "ColumnsPerGroup",
                                    "GroupsOfModules",
                                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                                    )

                if not "GroupGaps" in obj.PropertiesList:
                    obj.addProperty("App::PropertyIntegerList",
                                    "GroupGaps",
                                    "GroupsOfModules",
                                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                                    )

            else:
                if "ColumnsPerGroup" in obj.PropertiesList:
                    obj.removeProperty("ColumnsPerGroup")
                if "GroupGaps" in obj.PropertiesList:
                    obj.removeProperty("GroupGaps")

        '''
        # Properties that rotate the Modules:
        if prop == "Tilt":
            if len(obj.Shape.SubShapes) == 0:
                return

            all = obj.Shape.SubShapes[0]
            mainBean = all.SubShapes[1].SubShapes[0]
            faces = []
            minArea = min([face.Area for face in mainBean.Faces])
            for face in mainBean.Faces:
                if face.Area == minArea:
                    faces.append(face)
            axis = faces[0].CenterOfMass - faces[1].CenterOfMass
            center = faces[0].CenterOfMass
            print(center, " - ", axis)
            all.Placement.rotate(center, axis, obj.getPropertyByName(prop))
            obj.Shape = Part.makeCompound([all, obj.Shape.SubShapes[1]])

        # Properties that rotate the Poles:
        if prop == "Placement":
            if len(obj.Shape.SubShapes) == 0:
                return
            pl = obj.getPropertyByName(prop)
            angle = obj.Placement.Rotation.toEuler()[1]
            poles = obj.Shape.SubShapes[1].SubShapes
            newpoles = Part.makeCompound([])
            for pole in poles:
                center = pole.BoundBox.Center
                base = FreeCAD.Vector(center.x, center.y, pole.BoundBox.ZMax)
                newpoles.add(pole.rotate(base, FreeCAD.Vector(0, 1, 0), -angle))
            obj.Shape = Part.makeCompound([obj.Shape.SubShapes[0], newpoles])
    '''
        if prop in ['BeamHeight', 'BeamOffset', 'BeamSpacing', 'BeamWidth', 'MainBeamAxisPosition', 'MainBeamHeight',
                    'MainBeamWidth',
                    'ModuleColGap', 'ModuleCols', 'ModuleHeight', 'ModuleOffsetX', 'ModuleOffsetY', 'ModuleOrientation',
                    'ModuleRowGap', 'ModuleRows', 'ModuleThick', 'ModuleViews', 'ModuleWidth', 'MotorGap',
                    'AerialPole', 'DistancePole', 'NumberPole', 'PoleHeight', 'PoleLength', 'PoleWidth', 'ShowBeams']:

            self.changed = True
        else:
            self.changed = False
    def CalculateModuleArray(self, obj, totalh, totalw, moduleh, modulew):
        module = Part.makeBox(modulew, moduleh, obj.ModuleThick.Value)
        compound = Part.makeCompound([])
        offsetx = -totalw / 2
        offsety = -totalh / 2
        offsetz = obj.MainBeamHeight.Value + obj.BeamHeight.Value

        if obj.ModuleViews:
            mid = int(obj.ModuleCols.Value / 2)
            for row in range(int(obj.ModuleRows.Value)):
                for col in range(int(obj.ModuleCols.Value)):
                    xx = offsetx + (modulew + obj.ModuleColGap.Value) * col
                    if col >= mid:
                        xx += obj.MotorGap.Value - obj.ModuleColGap.Value
                    yy = offsety + (moduleh + obj.ModuleRowGap.Value) * row
                    zz = offsetz
                    moduleCopy = module.copy()
                    moduleCopy.Placement.Base = FreeCAD.Vector(xx, yy, zz)
                    compound.add(moduleCopy)
        else:
            totalArea = Part.makePlane(totalw, totalh)
            totalArea.Placement.Base = FreeCAD.Vector(offsetx, offsety, offsetz)
            compound.add(totalArea)
        return compound

    def calculateBeams(self, obj, totalh, totalw, moduleh, modulew):
        ''' make mainbeam and modules beams '''
        compound = Part.makeCompound([])
        mainbeam = Part.makeBox(totalw + obj.ModuleOffsetX.Value * 2,
                                obj.MainBeamWidth.Value,
                                obj.MainBeamHeight.Value)
        # details --------------------------------------------------------------------------------------------
        '''
        edg = []
        max_length = max([edge.Length for edge in mainbeam.Edges])
        for edge in mainbeam.Edges:
            if edge.Length == max_length:
                edg.append(edge)
        mainbeam = mainbeam.makeFillet(6, edg)
        tmp = Part.makeBox((totalw + obj.ModuleOffsetX.Value * 2) * 2, obj.MainBeamWidth.Value, obj.MainBeamHeight.Value)
        tmp.Placement.Base.x -= tmp.BoundBox.XLength / 4
        edg = []
        max_length = max([edge.Length for edge in tmp.Edges])
        for edge in tmp.Edges:
            if edge.Length == max_length:
                edg.append(edge)
        tmp = tmp.makeFillet(6, edg)
        tmp = tmp.makeOffsetShape(-3, 0.1)
        mainbeam = mainbeam.cut(tmp)
        '''
        # end details ----------------------------------------------------------------------------------------
        mainbeam.Placement.Base.x = -totalw / 2 - obj.ModuleOffsetX.Value
        mainbeam.Placement.Base.y = -obj.MainBeamWidth.Value / 2
        compound.add(mainbeam)

        # Correa profile:
        if obj.ShowBeams:  # TODO: make it in another function
            mid = int(obj.ModuleCols.Value / 2)

            up = 27.8  # todo
            thi = 3.2  # todo

            p1 = FreeCAD.Vector(obj.BeamWidth.Value / 2 - up, 0, thi)
            p2 = FreeCAD.Vector(p1.x, 0, obj.BeamHeight.Value)
            p3 = FreeCAD.Vector(obj.BeamWidth.Value / 2, 0, p2.z)
            p4 = FreeCAD.Vector(p3.x, 0, obj.BeamHeight.Value - thi)
            p5 = FreeCAD.Vector(p4.x - up + thi, 0, p4.z)
            p6 = FreeCAD.Vector(p5.x, 0, 0)

            p7 = FreeCAD.Vector(-p6.x, 0, p6.z)
            p8 = FreeCAD.Vector(-p5.x, 0, p5.z)
            p9 = FreeCAD.Vector(-p4.x, 0, p4.z)
            p10 = FreeCAD.Vector(-p3.x, 0, p3.z)
            p11 = FreeCAD.Vector(-p2.x, 0, p2.z)
            p12 = FreeCAD.Vector(-p1.x, 0, p1.z)

            p = Part.makePolygon([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p1])
            p = Part.Face(p)
            profile = p.extrude(FreeCAD.Vector(0, 428, 0))

            for col in range(int(obj.ModuleCols.Value)):
                xx = totalArea.Placement.Base.x + (modulew + obj.ModuleColGap.Value) * col
                if col >= mid:
                    xx += float(obj.MotorGap.Value) - obj.ModuleColGap.Value
                correaCopy = profile.copy()
                correaCopy.Placement.Base.x = xx
                correaCopy.Placement.Base.y = -428 / 2
                correaCopy.Placement.Base.z = obj.MainBeamHeight.Value
                self.ListModules.append(correaCopy)
                compound.add(correaCopy)

        return compound

    def CalculatePosts(self, obj, totalh, totalw):
        posttmp = Part.makeBox(obj.PoleWidth.Value, obj.PoleHeight.Value, obj.PoleLength.Value)
        compound = Part.makeCompound([])

        angle = obj.Placement.Rotation.toEuler()[1]
        offsetX = - totalw / 2
        offsetY = -obj.PoleHeight.Value / 2
        offsetZ = -(obj.PoleLength.Value - obj.AerialPole.Value)

        for x in range(int(obj.NumberPole.Value)):
            offsetX += obj.DistancePole[x] - obj.PoleWidth.Value / 2
            xx = offsetX
            yy = offsetY
            zz = offsetZ

            postCopy = posttmp.copy()
            postCopy.Placement.Base.x = xx
            postCopy.Placement.Base.y = yy
            postCopy.Placement.Base.z = zz
            base = FreeCAD.Vector(xx, yy, obj.PoleHeight.Value - offsetZ)
            postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
            compound.add(postCopy)
        return compound

    def rotateModules(self, obj, compound):
        ''''''

    def rotatePosts(self, obj):
        ''''''

    def execute(self, obj):
        # obj.Shape: compound
        # |- Modules and Beams: compound
        # |-- Modules array: compound
        # |--- Modules: solid
        # |-- Beams: compound
        # |--- MainBeam: solid
        # |--- Secundary Beams: solid (if exist)
        # |- Poles array: compound
        # |-- Poles: solid
        #
        # TODO: once you have done this structure you don´t need recompute everything,
        #       only the part you need

        if self.changed:
            self.changed = False
            pl = obj.Placement
            if obj.ModuleOrientation == "Portrait":
                w = obj.ModuleWidth.Value
                h = obj.ModuleHeight.Value
            else:
                h = obj.ModuleWidth.Value
                w = obj.ModuleHeight.Value

            totalh = h * obj.ModuleRows + obj.ModuleRowGap.Value * (obj.ModuleRows - 1)
            totalw = w * obj.ModuleCols + obj.ModuleColGap.Value * (obj.ModuleCols - 1) + \
                     (obj.MotorGap.Value - obj.ModuleColGap.Value) if obj.MotorGap.Value > 0 else 0

            modules = self.CalculateModuleArray(obj, totalh, totalw, h, w)
            beams = self.calculateBeams(obj, totalh, totalw, h, w)
            poles = self.CalculatePosts(obj, totalh, totalw)
            compound = Part.makeCompound([modules, beams])
            # TODO: change this to a independent function:
            compound.Placement.rotate(FreeCAD.Vector(0, 0, obj.BeamHeight.Value / 2),
                                      FreeCAD.Vector(1, 0, 0),
                                      obj.Tilt)
            compound.Placement.Base.z = obj.MainBeamAxisPosition.Value - (obj.MainBeamHeight.Value / 2)
            obj.Shape = Part.makeCompound([compound, poles])
            obj.Placement = pl
            obj.Width = min(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)
            obj.Length = max(obj.Shape.BoundBox.XLength, obj.Shape.BoundBox.YLength)

        angle = obj.Placement.Rotation.toEuler()[1]
        if (angle and angle > obj.MaxLengthwiseTilt) or \
           (angle < 0 and abs(angle) > abs(obj.MaxNegativeLengthwiseTilt)):
            obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
        else:
            obj.ViewObject.ShapeColor = (1.0, 1.0, 1.0)

class _ViewProviderTracker(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "solar-tracker.svg"))

    def setEdit(self, vobj, mode):
        """Method called when the document requests the object to enter edit mode.
        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].
        Just display the standard FRAME SETUP task panel.

        Parameters
        ----------
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].

        Returns
        -------
        bool
            If edit mode was entered.
        """

        if (mode == 0) and hasattr(self, "Object"):
            taskd = _TrackerTaskPanel(self.Object)
            taskd.obj = self.Object
            FreeCADGui.Control.showDialog(taskd)
            return True

        return False

class _TrackerTaskPanel:
    def __init__(self, obj=None):

        if not (obj is None):
            self.new = True
            self.obj = makeRack()
        else:
            self.new = False
            self.obj = obj

        # -------------------------------------------------------------------------------------------------------------
        # Module widget form
        # -------------------------------------------------------------------------------------------------------------
        self.formRack = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        if self.new:
            FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


class _FrameTaskPanel:

    def __init__(self, obj=None):

        if not (obj is None):
            self.new = True
            self.ojb = makeRack()
        else:
            self.new = False
            self.obj = obj

        self.formRack = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.setEnable(self.new)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        if self.new:
            FreeCADGui.Control.closeDialog()
        return True


class _CommandFixedRack:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-fixed.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantRack", "Fixed Rack"),
                'Accel': "R, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantRack",
                                                    "Creates a Fixed Rack object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        obj = makeRack()
        self.TaskPanel = _FixedRackTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return

class _CommandTrackerSetup:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "trackersetup.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTracker", "TrackerSetup"),
                'Accel': "R, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTracker",
                                                    "Creates a TrackerSetup object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        obj = makeTrackerSetup()
        self.TaskPanel = _FixedRackTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return

class _CommandTracker:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-tracker.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTracker", "Tracker"),
                'Accel': "R, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTracker",
                                                    "Creates a Tracker object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        setupobj = None
        for obj in sel:
            if obj.Name[:12] == "TrackerSetup":
                setupobj = obj
                break
        makeTracker(setup=setupobj)
        return

class _CommandMultiRowTracker:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-tracker.svg")),
                'MenuText': "Multi-row Tracker",
                'Accel': "R, M",
                'ToolTip': "Creates a multi-row Tracker object from trackers."}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        self.TaskPanel = _FixedRackTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return


if FreeCAD.GuiUp:
    class CommandRackGroup:

        def GetCommands(self):
            return tuple(['PVPlantFixedRack',
                          'PVPlantTrackerSetup',
                          'PVPlantTracker'
                          ])

        def GetResources(self):
            return {'MenuText': QT_TRANSLATE_NOOP("", 'Rack Types'),
                    'ToolTip': QT_TRANSLATE_NOOP("", 'Rack Types')
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None


    FreeCADGui.addCommand('PVPlantFixedRack', _CommandFixedRack())
    FreeCADGui.addCommand('PVPlantTrackerSetup', _CommandTrackerSetup())
    FreeCADGui.addCommand('PVPlantTracker', _CommandTracker())
    FreeCADGui.addCommand('Multirow', _CommandMultiRowTracker())
    FreeCADGui.addCommand('RackType', CommandRackGroup())

    '''# -*- coding: utf-8 -*-
# http://forum.freecadweb.org/viewtopic.php?f=22&t=16079
# creer une face autour des objets et la selectionner (ex rectangle face=true)
edges = []
for o in App.ActiveDocument.Objects:
#    print o.TypeId
    if str(o) !=  "<group object>":
        print o.Shape.ShapeType
        if (o.Shape.ShapeType == 'Edge') or (o.Shape.ShapeType == 'Wire'):
            edges.append(o.Shape)

fusion_wire = edges[0]
for no, e in enumerate(edges):
    no += 1
    if no > 1:
        fusion_wire = fusion_wire.fuse(e)

ex = fusion_wire.extrude(FreeCAD.Vector(0,0,5))
FreeCAD.ActiveDocument.recompute()

sel = FreeCADGui.Selection.getSelection()
#print str(sel[0].Shape.ShapeType)
slab = App.ActiveDocument.getObject(sel[0].Name).Shape.cut(ex)

for f in slab.Faces:
    Part.show(f)'''
