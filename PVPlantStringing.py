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
import PVPlantRack

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

    try:
        if FreeCAD.ActiveDocument.StringsSetup:
            FreeCAD.ActiveDocument.StringsSetup.addObject(obj)
    except:
        pass
    return obj

class _StringSetup:
    def __init__(self, obj):
        self.setCommonProperties(obj)
        self.obj = obj
        self.StringCount = 1

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
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        self.setProperties(obj)

    def addString(self, modulelist):
        stringName = "String" + str(self.StringCount)
        self.obj.addProperty("App::PropertyIntegerList",
                             stringName,
                             "Setup",
                             "String: " + stringName
                             )
        setattr(self.obj, stringName, modulelist)

        '''
        self.obj.addProperty("App::PropertyInteger",
                             stringName + "_Power",
                             "Outputs",
                             QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                             )
        setattr(self.obj, stringName + "_Power", len(modulelist) * 450)
        '''
        self.obj.NumberOfStrings = self.StringCount
        self.StringCount += 1


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

class _SelObserver:
    def __init__(self, form):
        self.form = form

    def addSelection(self, doc, obj, sub, pnt):
        rack = FreeCAD.ActiveDocument.getObjectsByLabel(obj)[0].Shape
        modules = rack.SubShapes[0].SubShapes[0].SubShapes
        if sub[0:4] == 'Face':
            numFace = int(sub.replace('Face', '')) - 1
            selFace = rack.Faces[numFace]
            for module in modules:
                for num, face in enumerate(module.Faces):
                    if selFace.isSame(face):
                        self.form.setModule(modules.index(module))
                        FreeCADGui.Selection
                        return True

        elif sub[0:4] == 'Edge':
            numEdge = int(sub.replace('Edge', '')) - 1
            selEdge = rack.Edge[numEdge]
            for module in modules:
                for num, edge in enumerate(module.Edges):
                    if selEdge.isSame(edge):
                        print("Encontrado: ", modules.index(module))
                        return True
        return True

    def removeSelection(self, doc, obj, sub):  # Delete the selected object
        '''print("FSO-RemSel:" + str(obj) + ":" + str(sub) + "\n")'''
        return True

    def setSelection(self, doc):  # Selection in ComboView
        '''print("FSO-SetSel:" + "\n")'''
        return True

    def clearSelection(self, doc):  # If click on the screen, clear the selection
        '''print("FSO-ClrSel:" + "\n")'''
        return True

class _StringSetupPanel:
    def __init__(self, obj=None):
        self.obj = obj
        self.new = False

        if obj is None:
            self.new = True
            self.obj = makeStringSetup()

        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantStringSetup.ui")
        self.form.buttonSelFrame.clicked.connect(self.selFrame)
        self.form.buttonAddString.clicked.connect(self.addString)
        self.form.listStrings.currentRowChanged.connect(self.listStringsCurrentRowChanged)
        self.form.editName.editingFinished.connect(self.setStringName)

        self.selobserver = _SelObserver(self)
        self.stringslist = []
        self.currentstring = 0
        self.totalModules = 0
        self.left = 0

        self.frameColor = None

    def selFrame(self):
        sel = FreeCADGui.Selection.getSelection()
        frame = None
        if len(sel) == 0:
            # TODO: lanzar un error
            return
        elif len(sel) == 1:
            frame = sel[0]
        else:
            for obj in sel:
                if not hasattr(obj, 'Proxy'):
                    continue
                print(obj.Proxy.__class__)
                print(issubclass(obj.Proxy.__class__, PVPlantRack._Frame))
                if issubclass(obj.Proxy.__class__, PVPlantRack._Frame):
                    frame = obj
                    break

        if frame == None:
            # TODO: lanzar un error
            print("No frame selected")
            return

        self.frame = frame
        self.form.editFrame.setText(frame.Label)
        self.totalModules = frame.ModuleCols * frame.ModuleRows
        self.left = self.totalModules
        self.form.editTotal.setText(str(int(self.totalModules)))
        self.form.editUsed.setText("0")
        self.form.editLeft.setText(str(int(self.left)))

        FreeCADGui.Selection.removeObserver(self.selobserver)
        FreeCADGui.Selection.addObserver(self.selobserver)

        self.frameColor = self.obj.ViewObject.ShapeColor
        self.colorlist = []
        for face in self.frame.Shape.Faces:
            self.colorlist.append((1.0, 0.50, 0.40, 0.25))
        self.frame.ViewObject.DiffuseColor = self.colorlist

    def addString(self):
        FreeCADGui.Selection.clearSelection()
        self.stringslist.append([])
        self.currentstring = len(self.stringslist) - 1
        self.form.listStrings.addItem("String" + str(self.form.listStrings.count()))
        self.form.listStrings.setCurrentRow(self.form.listStrings.count() - 1)

    def listStringsCurrentRowChanged(self, row):
        self.currentstring = row
        self.form.listModules.clear()
        for num in self.stringslist[row]:
            self.form.listModules.addItem(str(num))

    def setModule(self, numModule):
        if len(self.stringslist) == 0:
            return

        if self.left == 0:
            return

        if numModule in self.stringslist[self.currentstring]:
            '''remove module ?? '''
            self.stringslist[self.currentstring].remove(int(numModule))
            item = self.form.listModules.findItems(str(numModule), QtCore.Qt.MatchExactly)[0]
            self.form.listModules.takeItem(self.form.listModules.row(item))
            for moduleFace in self.frame.Shape.Solids[numModule].Faces:
                for i, face in enumerate(self.frame.Shape.Faces):
                    if moduleFace.isEqual(face):
                        self.colorlist[i] = (1.0, 0.50, 0.40, 0.25)
                        self.frame.ViewObject.DiffuseColor = self.colorlist
                        break
        else:
            self.stringslist[self.currentstring].append(int(numModule))
            self.form.listModules.addItem(str(numModule))
            for moduleFace in self.frame.Shape.Solids[numModule].Faces:
                for i, face in enumerate(self.frame.Shape.Faces):
                    if moduleFace.isEqual(face):
                        self.colorlist[i] = (0.0, 0.0, 1.0, 0.0)
                        self.frame.ViewObject.DiffuseColor = self.colorlist
                        break

        self.calculateModules()

    def calculateModules(self):
        num = 0
        for string in self.stringslist:
            num += len(string)

        self.left = int(self.totalModules - num)
        self.form.editUsed.setText(str(num))
        self.form.editLeft.setText(str(self.left))

    def setStringName(self):
        self.obj.Label = self.form.editName.text()

    def accept(self):
        for string in self.stringslist:
            self.obj.Proxy.addString(string.copy())
        self.FormClosing()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        self.FormClosing()
        return True

    def FormClosing(self):
        FreeCADGui.Selection.removeObserver(self.selobserver)
        FreeCADGui.Control.closeDialog()
        self.frame.ViewObject.DiffuseColor = self.frameColor

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

    def onBeforeChange(self, obj, prop):
        ''''''
        print(prop)
        print(obj.getPropertyByName(prop))

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

                vec = None
                if obj.Frame.Route:
                    vertexes = obj.Frame.Route.Shape.Vertexes
                    vec = vertexes[1].Point - vertexes[0].Point
                else:
                    poles = obj.Frame.Shape.SubShapes[1].SubShapes
                    vec = poles[1].BoundBox.Center - poles[0].BoundBox.Center
                vecp= FreeCAD.Vector(-vec.y, vec.x, vec.z)
            # V1:
            for stringnum in range(obj.StringSetup.NumberOfStrings):
                ''''''

            return
            # V0:
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


