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
import Part
import math

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt, txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import os
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
import PVPlantResources
from PVPlantResources import DirIcons as DirIcons
Dir3dObjects = os.path.join(PVPlantResources.DirResources, "3dObjects")

def makeStringSetup():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "StringSetup")
    _StringSetup(obj)
    _ViewProviderStringSetup(obj.ViewObject)

    if FreeCAD.ActiveDocument.StringsSetup:
        FreeCAD.ActiveDocument.StringsSetup.addObject(obj)

    FreeCAD.ActiveDocument.recompute()

    return obj

class _StringSetup:
    def __init__(self, obj):
        self.setCommonProperties(obj)
        self.obj = obj
        self.StringCount = 1

        # test:
        self.addString([27, 25, 23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1,
                        0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26])
        self.addString([29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55,
                        54, 52, 50, 48, 46, 44, 42, 30, 38, 36, 34, 32, 30, 28])

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("NumberOfStrings" in pl):
            obj.addProperty("App::PropertyInteger",
                            "NumberOfStrings",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).NumberOfStrings = 0
            obj.setEditorMode("NumberOfStrings", 1)

        self.Type = "StringSetup"

    def addString(self, modulelist):
        stringName = "String" + str(self.StringCount)
        self.obj.addProperty("App::PropertyIntegerList",
                             stringName,
                             "Setup",
                             QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                             )
        setattr(self.obj, stringName, modulelist)
        self.obj.NumberOfStrings = self.StringCount
        self.StringCount += 1

        '''
        ['App::PropertyBool', 
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
         'Points::PropertyGreyValue', 
         'Points::PropertyGreyValueList', 
         'Points::PropertyNormalList',
         'Points::PropertyCurvatureList', 
         'Points::PropertyPointKernel', 
         'Mesh::PropertyNormalList',
         'Mesh::PropertyCurvatureList', 
         'Mesh::PropertyMeshKernel']
         '''

class _ViewProviderStringSetup:
    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''

        return str(os.path.join(DirIcons, "stringsetup.svg"))
    '''
    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group
    '''

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None

    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None

class _StringSetupPanel:
    def __init__(self, obj=None):

        if obj is None:
            self.new = True
            self.obj = makeStringSetup()
        else:
            self.new = False
            self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantStringSetup.ui")

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        if self.new:
            FreeCADGui.Control.closeDialog()
        return True





def makeString(base=None):
    if base is None:
        return
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "String")
    _String(obj)
    obj.Frame = base
    _ViewProviderString(obj.ViewObject)

    if FreeCAD.ActiveDocument.Strings:
        FreeCAD.ActiveDocument.Strings.addObject(obj)

    FreeCAD.ActiveDocument.recompute()
    return obj

class _String(ArchComponent.Component):
    def __init__(self, obj):

        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)

        obj.Proxy = self
        obj.IfcType = "Cable Segment"
        obj.setEditorMode("IfcType", 1)

    def setProperties(self, obj):

        pl = obj.PropertiesList
        if not ("Frame" in pl):
            obj.addProperty("App::PropertyLink",
                            "Frame",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).Frame = None

        if not ("StringSetup" in pl):
            obj.addProperty("App::PropertyLink",
                            "StringSetup",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).StringSetup = None

        if not ("StringPoles" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "StringPoles",
                            "StringOutput",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).StringPoles = []
            obj.setEditorMode("StringPoles", 1)

        self.Type = "String"

    def onDocumentRestored(self, obj):
        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)
        obj.Proxy = self

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

        def getDownFace(module):
            area_max = max([face.Area for face in module.Faces])
            faces = []
            for face in module.Faces:
                if face.Area == area_max:
                    faces.append(face)
            return faces[0] if faces[0].Placement.Base.z > faces[1].Placement.Base.z else faces[1]

        if (prop == "Frame") or (prop == "StringSetup"):
            if not (obj.Frame is None) and not (obj.StringSetup is None):
                JuntionBoxPosition = 200
                portrait = obj.Frame.ModuleOrientation == "Portrait"

                cableLength = 1200
                if hasattr(obj.Frame, "PoleCableLength"):
                    cableLength = obj.Frame.PoleCableLength.Value

                moduleWidth = obj.Frame.ModuleWidth.Value
                moduleHeight = obj.Frame.ModuleHeight.Value
                dist_x = JuntionBoxPosition + obj.Frame.ModuleColGap.Value + (
                    moduleWidth if portrait else moduleHeight) / 2
                dist_y = obj.Frame.ModuleRowGap.Value + (moduleHeight if portrait else moduleWidth)

                PolePosition = 0
                if portrait:
                    PolePosition = moduleWidth / 2 - JuntionBoxPosition

                FrameModules = obj.Frame.Shape.SubShapes[0].SubShapes[0].SubShapes
                cableProfile = Part.Face(Part.Wire(Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 6).toShape()))
                positiveMC4 = Part.Shape()
                positiveMC4.read(os.path.join(Dir3dObjects, "MC4 POSITIVE.IGS"))
                negativeMC4 = Part.Shape()
                negativeMC4.read(os.path.join(Dir3dObjects, "MC4 NEGATIVE.IGS"))

                for stringnum in range(obj.StringSetup.NumberOfStrings):
                    string = obj.StringSetup.getPropertyByName("String" + str(stringnum + 1))
                    total = len(string) - 1
                    dir = 0
                    ndir = 0
                    # dirvec = FrameModules(string[-]).Placement.Base - FrameModules(string[0]).Placement.Base
                    for i, num in enumerate(string):
                        face = getDownFace(FrameModules[num])

                        if i < total:
                            dir = string[i + 1] - num
                            dir /= abs(dir)
                            ndir = -dir

                        positivePolePosition = FreeCAD.Vector(0, ndir * PolePosition, 0) + face.CenterOfMass
                        negativePolePosition = FreeCAD.Vector(0, dir * PolePosition, 0) + face.CenterOfMass

                        # dibujar +:
                        p1 = positivePolePosition
                        p2 = p1 + ndir * FreeCAD.Vector(0, 50, 0)
                        p3 = p2 + ndir * FreeCAD.Vector(cableLength - dist_x, 0, 0)
                        p4 = p3 + ndir * FreeCAD.Vector(0, dist_x - 50, 0)
                        w = Part.makePolygon([p1, p2, p3, p4])
                        #cableProfile.Placement.Base = p1
                        #cable = w.makePipeShell([cableProfile], True, False, 2)
                        Part.show(w)
                        mc4copy = positiveMC4.copy()
                        mc4copy.Placement.Base = p4 + FreeCAD.Vector(0, mc4copy.BoundBox.XLength/2 + 1.3, 0)
                        positiveMC4.Placement.Rotation.Angle = math.radians(ndir * 90)
                        Part.show(mc4copy)

                        # dibujar -:
                        p1 = negativePolePosition
                        p2 = p1 + dir * FreeCAD.Vector(0, 50, 0)
                        p3 = p2 + ndir * FreeCAD.Vector(cableLength - dist_x, 0, 0)
                        p4 = p3 + dir * FreeCAD.Vector(0, dist_x - 50, 0)
                        w = Part.makePolygon([p1, p2, p3, p4])
                        Part.show(w)
                        mc4copy = negativeMC4.copy()
                        mc4copy.Placement.Base = p4 - FreeCAD.Vector(0, mc4copy.BoundBox.XLength/2 + 1.3, 0)
                        mc4copy.Placement.Rotation.Angle = math.radians(dir * 90)
                        Part.show(mc4copy)

                        if i == 0 or i == total:
                            list = obj.StringPoles.copy()
                            list.append(p3)
                            obj.StringPoles = list
                    break

    def execute(self, obj):
        '''Do something when recompute'''


class _ViewProviderString(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "string.svg"))



class _CommandStringSetup:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "stringsetup.svg")),
                'Accel': "E, C",
                'MenuText': "String Setup",
                'ToolTip': "Configure strings of a Frame"}

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        self.TaskPanel = _StringSetupPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return

class _CommandStringing:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "string.svg")),
                'Accel': "E, S",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "String"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Make string on a Frame")}

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        # issubclass(Car, Vehicles)
        # isinstance(Car, Vehicles)
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            for obj in sel:
                if obj.Name.__contains__("Tracker"):
                    makeString(obj)


if FreeCAD.GuiUp:
    class _CommandStringingGroup:

        def GetCommands(self):
            return tuple(['PVPlantStringSetup',
                          'PVPlantStringing'
                          ])

        def GetResources(self):
            return {'MenuText': 'Stringing',
                    'ToolTip': 'Tools to setup and make strings'
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None

    FreeCADGui.addCommand('PVPlantStringSetup', _CommandStringSetup())
    FreeCADGui.addCommand('PVPlantStringing', _CommandStringing())
    FreeCADGui.addCommand('Stringing', _CommandStringingGroup())


