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


class _Frame(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setCommonProperties(obj)

        # Does a IfcType exist?
        obj.IfcType = "Structural Item"
        obj.setEditorMode("IfcType", 1)

        self.totalAreaShape = None
        self.changed = True

    def setCommonProperties(self, obj):
        # Definicion de Propiedades:
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
        if not "MotorGap" in pl:
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

        if not "Modules" in pl:
            obj.addProperty("App::PropertyLinkSubListChild",
                            "Modules",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property",
                                              "The facemaker type to use to build the profile of this object")
                            ).ModuleViews = True

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
        self.Type = "Frame"

        '''[
                 'App::PropertyBool',
                 'App::PropertyBoolList', 
                 'App::PropertyFloat', 
                 'App::PropertyFloatList', 
                 'App::PropertyFloatConstraint', 
                 'App::PropertyPrecision', 
                 'App::PropertyQuantity', 
                 'App::PropertyQuantityConstraint', 
                 'App::PropertyAngle', 
                 'App::PropertyDistance', 
                 'App::PropertyLength', 
                 'App::PropertyArea', 
                 'App::PropertyVolume', 
                 'App::PropertyFrequency', 
                 'App::PropertySpeed', 
                 'App::PropertyAcceleration', 
                 'App::PropertyForce',
                 'App::PropertyPressure',
                 'App::PropertyVacuumPermittivity', 
                 'App::PropertyInteger', 
                 'App::PropertyIntegerConstraint', 
                 'App::PropertyPercent', 
                 'App::PropertyEnumeration', 
                 'App::PropertyIntegerList', 
                 'App::PropertyIntegerSet', 
                 'App::PropertyMap', 
                 'App::PropertyString', 
                 'App::PropertyPersistentObject', 
                 'App::PropertyUUID', 
                 'App::PropertyFont', 
                 'App::PropertyStringList', 
                 'App::PropertyLink', 
                 'App::PropertyLinkChild', 
                 'App::PropertyLinkGlobal', 
                 'App::PropertyLinkHidden', 
                 'App::PropertyLinkSub', 
                 'App::PropertyLinkSubChild', 
                 'App::PropertyLinkSubGlobal', 
                 'App::PropertyLinkSubHidden', 
                 'App::PropertyLinkList', 
                 'App::PropertyLinkListChild', 
                 'App::PropertyLinkListGlobal', 
                 'App::PropertyLinkListHidden', 
                 'App::PropertyLinkSubList', 
                 'App::PropertyLinkSubListChild', 
                 'App::PropertyLinkSubListGlobal', 
                 'App::PropertyLinkSubListHidden', 
                 'App::PropertyXLink', 
                 'App::PropertyXLinkSub', 
                 'App::PropertyXLinkSubList', 
                 'App::PropertyXLinkList', 
                 'App::PropertyMatrix', 
                 'App::PropertyVector', 
                 'App::PropertyVectorDistance', 
                 'App::PropertyPosition', 
                 'App::PropertyDirection', 
                 'App::PropertyVectorList', 
                 'App::PropertyPlacement', 
                 'App::PropertyPlacementList', 
                 'App::PropertyPlacementLink', 
                 'App::PropertyColor', 
                 'App::PropertyColorList', 
                 'App::PropertyMaterial', 
                 'App::PropertyMaterialList', 
                 'App::PropertyPath', 
                 'App::PropertyFile', 
                 'App::PropertyFileIncluded', 
                 'App::PropertyPythonObject', 
                 'App::PropertyExpressionEngine', 
                 'Part::PropertyPartShape', 
                 'Part::PropertyGeometryList', 
                 'Part::PropertyShapeHistory', 
                 'Part::PropertyFilletEdges', 
                 'Mesh::PropertyNormalList', 
                 'Mesh::PropertyCurvatureList', 
                 'Mesh::PropertyMeshKernel', 
                 'Sketcher::PropertyConstraintList']
        '''

    def getTotalAreaShape(self):
        return self.totalAreaShape


''' ------------------------------------------- Fixed Structure --------------------------------------------------- '''


def makeRack(name="Rack"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _FixedRack(obj)
    _ViewProviderFixedRack(obj.ViewObject)
    # FreeCAD.ActiveDocument.recompute()
    return obj


class _FixedRack(_Frame):
    "A Fixed Rack Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        _Frame.__init__(self, obj)
        _Frame.setProperties(self, obj)
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


def makeTracker(name="Tracker"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Tracker")
    obj.Label = name
    _Tracker(obj)
    _ViewProviderTracker(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    site = PVPlantSite.get()
    frame_list = site.Frames
    frame_list.append(obj)
    site.Frames = frame_list

    return obj


class _Tracker(_Frame):
    "A 1 Axis Tracker Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        _Frame.__init__(self, obj)
        self.setProperties(obj)
        obj.Proxy = self

        obj.ModuleCols = 45
        obj.ModuleRows = 2
        obj.ModuleColGap = 20
        obj.ModuleRowGap = 20
        obj.Tilt = 0

    def setProperties(self, obj):
        pl = obj.PropertiesList

        # Array de modulos: -------------------------------------------------------------------------------------------
        if not "MotorGap" in pl:
            obj.addProperty("App::PropertyDistance",
                            "MotorGap",
                            "Posicion de modulos",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).MotorGap = 550

        # Poles: ------------------------------------------------------------------------------------------------------
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
            obj.addProperty("App::PropertyFloatList",  # No list of Lenght so I use float list
                            "DistancePole",
                            "Poles",
                            "Distance between poles starting from the left and from the first photovoltaic module "
                            "without taking into account the offsets"
                            ).DistancePole = [1500.0, 3000.0, 7000.0, 7000.0, 7000.0, 7000.0, 7000.0]

        if not "AerialPole" in pl:
            obj.addProperty("App::PropertyLength",
                            "AerialPole",
                            "Poles",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).AerialPole = 1050

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

        self.Type = "1 Axis Tracker"

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and Arch wall properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)
        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

        '''
        ['Additions', 'AerialPole', 'Axis', 'Base', 'BeamHeight', 'BeamOffset', 'BeamSpacing', 'BeamWidth', 'CloneOf', 
        'Description', 'DistancePole', 'ExpressionEngine', 'HiRes', 'HorizontalArea', 'IfcData', 'IfcProperties', 
        'IfcType', 'Label', 'Label2', 'Length', 'MainBeamAxisPosition', 'MainBeamHeight', 'MainBeamWidth', 'Material', 
        'MaxLengthwiseTilt', 'MaxPhi', 'MinPhi', 'ModuleColGap', 'ModuleCols', 'ModuleHeight', 'ModuleOffsetX', 
        'ModuleOffsetY', 'ModuleOrientation', 'ModulePower', 'ModuleRowGap', 'ModuleRows', 'ModuleThick', 'ModuleViews',
        'ModuleWidth', 'Modules', 'MotorGap', 'MoveBase', 'MoveWithHost', 'NumberPole', 'PerimeterLength', 'Placement',
        'PoleCableLength', 'PoleHeight', 'PoleLength', 'PoleWidth', 'Proxy', 'Shape', 'ShowBeams', 'StandardCode', 
        'Subtractions', 'Tag', 'Tilt', 'TotalAreaShape', 'VerticalArea', 'Visibility', 'Width']
        '''

        self.changed = True
        '''
        if prop in ['BeamHeight', 'BeamOffset', 'BeamSpacing', 'BeamWidth', 'MainBeamAxisPosition', 'MainBeamHeight', 'MainBeamWidth',
                    'ModuleColGap', 'ModuleCols', 'ModuleHeight', 'ModuleOffsetX', 'ModuleOffsetY', 'ModuleOrientation',
                    'ModuleRowGap', 'ModuleRows', 'ModuleThick', 'ModuleViews', 'ModuleWidth', 'MotorGap',
                    'AerialPole', 'DistancePole',
                    'NumberPole', 'PoleHeight', 'PoleLength', 'PoleWidth', 'ShowBeams']:

            self.changed = True

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

    def execute(self, obj):
        # obj.Shape = compound
        # |- Modules and Beams = compound
        # |-- Modules array: compound
        # |___ Modules: solid
        # |-- Beams
        # |--- MainBeam: solid
        # |--- Secundary Beams: solid
        # |- Poles array: compound
        # |-- Poles: solid
        #
        # once you have done this structure you don´t need recompute everything, only the part you need

        print(" -----   Execute: ", self.changed)
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
            obj.Width = totalw + obj.ModuleOffsetX.Value * 2
            obj.Length = totalh

            modules = self.CalculateModuleArray(obj, totalh, totalw, h, w)
            beams = self.calculateBeams(obj, totalh, totalw, h, w)
            poles = self.CalculatePosts(obj, totalh, totalw)
            compound = Part.makeCompound([modules, beams])
            compound.Placement.rotate(FreeCAD.Vector(0, 0, obj.MainBeamAxisPosition.Value),
                                      FreeCAD.Vector(1, 0, 0),
                                      obj.Tilt)
            compound.Placement.Base.z = obj.MainBeamAxisPosition.Value - (obj.MainBeamHeight.Value / 2)
            obj.Shape = Part.makeCompound([compound, poles])
            obj.Placement = pl

            angle = obj.Placement.Rotation.toEuler()[1]
            if angle > obj.MaxLengthwiseTilt:
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
            taskd = _TrackerTaskPanel(self.Object)
            taskd.obj = self.Object
            # taskd.update()
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
        obj = makeTracker()
        self.TaskPanel = _FixedRackTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return


if FreeCAD.GuiUp:
    class CommandRackGroup:

        def GetCommands(self):
            return tuple(['PVPlantFixedRack',
                          'PVPlantTracker'
                          ])

        def GetResources(self):
            return {'MenuText': QT_TRANSLATE_NOOP("", 'Rack Types'),
                    'ToolTip': QT_TRANSLATE_NOOP("", 'Rack Types')
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None


    FreeCADGui.addCommand('PVPlantFixedRack', _CommandFixedRack())
    FreeCADGui.addCommand('PVPlantTracker', _CommandTracker())
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
