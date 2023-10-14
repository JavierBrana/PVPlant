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
import Part
import PVPlantSite
import Utils.PVPlantUtils as utils
import MeshPart as mp

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond

import os
from PVPlantResources import DirIcons as DirIcons

__title__ = "PVPlant Areas"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons
Dir3dObjects = os.path.join(PVPlantResources.DirResources, "3dObjects")

''' Default Area: '''
def makeArea(points = None, type = 0):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Area")
    if type == 0:
        _Area(obj)
        _ViewProviderArea(obj.ViewObject)
    elif type == 1:
        _ForbiddenArea(obj)
        _ViewProviderForbiddenArea(obj.ViewObject)
    if points:
        obj.Points = points
    return obj

class _Area:
    def __init__(self, obj):
        ''' Initialize the Area object '''
        self.Type = None
        self.obj = None

    def setProperties(self, obj):
        pl = obj.PropertiesList

        if not ("Base" in pl):
            obj.addProperty("App::PropertyLink",
                            "Base",
                            "Area",
                            "Base wire"
                            ).Base = None

        if not ("Type" in pl):
            obj.addProperty("App::PropertyString",
                            "Type",
                            "Area",
                            "Points that define the area"
                            ).Type = "Area"

        obj.setEditorMode("Type", 1)

        self.Type = obj.Type
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        """ Method run when the document is restored """
        self.setProperties(obj)

class _ViewProviderArea:
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

        return str(os.path.join(DirIcons, "area.svg"))
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

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        return None


''' Frame Area '''
def makeFramedArea(base = None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "FrameArea")
    FrameArea(obj)
    ViewProviderFrameArea(obj.ViewObject)
    if base:
        obj.Base = base
    try:
        group = FreeCAD.ActiveDocument.FrameZones
    except:
        group = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'FrameZones')
        group.Label = "FrameZones"
    group.addObject(obj)

    return obj

class FrameArea(_Area):
    def __init__(self, obj):
        _Area.__init__(self, obj)
        self.setProperties(obj)
        self.obj = None

    def setProperties(self, obj):
        _Area.setProperties(self, obj)
        pl = obj.PropertiesList

        if not ("Frames" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Frames",
                            "Area",
                            "All the frames inside this area."
                            )

        self.Type = "Area"
        obj.Proxy = self
        self.obj = obj

    def onDocumentRestored(self, obj):
        """Method run when the document is restored."""
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        if prop == "Base":
            if obj.Base.Shape is None:
                obj.Shape = Part.Shape()
                return

            import Utils.PVPlantUtils as utils

            base = obj.Base.Shape
            land = PVPlantSite.get().Terrain.Mesh
            vec = FreeCAD.Vector(0,0,1)
            wire = utils.getProjected(base, vec)
            tmp = mp.projectShapeOnMesh(wire, land, vec)
            shape = Part.makeCompound([])
            for section in tmp:
                shape.add(Part.makePolygon(section))
            obj.Shape = shape

    def addFrame(self, frame):
        list = self.obj.Frames.copy()
        list.append(frame)
        self.obj.Frames = sorted(list, key=lambda x: x.Name)

    def execute(self, obj):
        ''' execute '''
        #_Area.execute(self, obj)

class ViewProviderFrameArea:
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

        return str(os.path.join(DirIcons, "FrameArea.svg"))

    def claimChildren(self):
        """ Provides object grouping """
        children = []
        if self.Object.Base:
            children.append(self.Object.Base)
        return children

    '''def setEdit(self, vobj, mode=0):
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
        pass'''

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        return None


''' offsets '''
def makeOffsetArea(base = None, val=None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "OffsetArea")
    OffsetArea(obj)
    obj.Base = base
    ViewProviderOffsetArea(obj.ViewObject)
    if val:
        obj.Distance = val

    offsets = None
    try:
        offsetsgroup = FreeCAD.ActiveDocument.Offsets
    except:
        offsetsgroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Offsets')
        offsetsgroup.Label = "Offsets"
    offsetsgroup.addObject(obj)

    return obj

class OffsetArea(_Area):
    def __init__(self, obj):
        _Area.__init__(self, obj)
        self.setProperties(obj)

    def setProperties(self, obj):
        _Area.setProperties(self, obj)
        pl = obj.PropertiesList
        if not ("OffsetDistance" in pl):
            obj.addProperty("App::PropertyDistance",
                            "OffsetDistance",
                            "OffsetArea",
                            "Base wire"
                            )

        self.Type = obj.Type = "Area_Offset"

    def onDocumentRestored(self, obj):
        """Method run when the document is restored."""
        self.setProperties(obj)

    def execute(self, obj):
        import Utils.PVPlantUtils as utils

        base = obj.Base.Shape
        land = PVPlantSite.get().Terrain.Mesh
        vec = FreeCAD.Vector(0, 0, 1)
        wire = utils.getProjected(base, vec)

        ''' makeOffset2D(offset, join = 0, fill = False, openResult = false, intersection = false)
         * offset: distance to expand the shape by.
         * join: method of offsetting non-tangent joints. 0 = arcs, 1 = tangent, 2 = intersection
         * fill: if true, the output is a face filling the space covered by offset. If false, the output is a wire/face.
         * openResult: True for "Skin" mode; False for Pipe mode.
         * intersection: collective offset'''

        wire = wire.makeOffset2D(obj.OffsetDistance.Value, 2, False, False, True)
        tmp = mp.projectShapeOnMesh(wire, land, vec)
        shape = Part.makeCompound([])
        for section in tmp:
            shape.add(Part.makePolygon(section))
        obj.Shape = shape

class ViewProviderOffsetArea(_ViewProviderArea):
    def getIcon(self):
        ''' Return object treeview icon. '''
        return str(os.path.join(DirIcons, "offset.svg"))

    def claimChildren(self):
        """ Provides object grouping """
        children = []
        if self.Object.Base:
            children.append(self.Object.Base)
        return children

''' Forbidden Area: '''
def makeProhibitedArea(base = None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "ProhibitedArea")
    ProhibitedArea(obj)
    ViewProviderForbiddenArea(obj.ViewObject)
    if base:
        obj.Base = base
    try:
        group = FreeCAD.ActiveDocument.Exclusion
    except:
        group = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Exclusion')
        group.Label = "Exclusion"
    group.addObject(obj)

    return obj

class ProhibitedArea(OffsetArea):
    def __init__(self, obj):
        OffsetArea.__init__(self, obj)
        self.setProperties(obj)

    def setProperties(self, obj):
        OffsetArea.setProperties(self, obj)
        self.Type = obj.Type = "ProhibitedArea"
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        """Method run when the document is restored."""
        self.setProperties(obj)

class ViewProviderForbiddenArea(_ViewProviderArea):
    def getIcon(self):
        ''' Return object treeview icon '''
        return str(os.path.join(DirIcons, "area_forbidden.svg"))

    def claimChildren(self):
        """ Provides object grouping """
        children = []
        if self.Object.Base:
            children.append(self.Object.Base)
        return children


''' PV Area: '''
def makePVSubplant():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "PVSubplant")
    PVSubplant(obj)
    ViewProviderPVSubplant(obj.ViewObject)
    return obj

class PVSubplant:
    def __init__(self, obj):
        self.setProperties(obj)
        self.Type = None
        self.obj = None

    def setProperties(self, obj):
        pl = obj.PropertiesList

        if not "Type" in pl:
            obj.addProperty("App::PropertyString",
                            "Type",
                            "Base",
                            "The facemaker type to use to build the profile of this object"
                            ).Type = "PVSubplant"
        obj.setEditorMode("Type", 1)

        if not ("Frames" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Frames",
                            "PVSubplant",
                            "List of frames"
                            )

        if not ("Inverters" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Inverters",
                            "PVSubplant",
                            "List of Inverters"
                            )

        if not ("StringBoxes" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "StringBoxes",
                            "PVSubplant",
                            "List of String-Boxes"
                            )
        if not ("Cables" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Cables",
                            "PVSubplant",
                            "List of Cables"
                            )

        if not "TotalPVModules" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "TotalPVModules",
                            "PVSubplant",
                            "The facemaker type to use to build the profile of this object"
                            )

        if not "TotalPowerDC" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "TotalPowerDC",
                            "PVSubplant",
                            "The facemaker type to use to build the profile of this object"
                            )

        self.Type = obj.Type
        self.obj = obj
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        """Method run when the document is restored."""
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        if prop == "Frames":
            import numpy as np
            # 1. Dibujar contorno:
            maxdist = 6000
            if len(obj.Frames) > 0:
                onlyframes = []
                for object in obj.Frames:
                    if object.Name.startswith("Tracker"):
                        onlyframes.append(object)
                obj.Frames = onlyframes

                pts = []
                for frame in obj.Frames:
                    for panel in frame.Shape.SubShapes[0].SubShapes[0].SubShapes:
                        zm = panel.BoundBox.ZMax
                        for i in range(8):
                            pt = panel.BoundBox.getPoint(i)
                            if pt.z == zm:
                                pts.append(pt)
                import MeshTools.Triangulation as Triangulation
                import MeshTools.MeshGetBoundary as mgb
                m = Triangulation.Triangulate(np.array(pts), MaxlengthLE=maxdist, use3d=False)
                b = mgb.get_boundary(m)
                obj.Shape = b

                # 2. rellenar información
                power = 0
                modulenum = 0
                for frame in obj.Frames:
                    modules = frame.Setup.ModuleColumns * frame.Setup.ModuleRows
                    power += frame.Setup.ModulePower.Value * modules
                    modulenum += modules
                obj.TotalPowerDC = power
                obj.TotalPVModules = modulenum

    def addObject(self, obj):
        ''' add object, do a filter and put it in the correct list '''

    def execute(self, obj):
        ''''''

class ViewProviderPVSubplant:
    def __init__(self, vobj):
        ''' Set view properties. '''
        self.Object = None
        vobj.Proxy = self

    def attach(self, vobj):
        ''' Create Object visuals in 3D view. '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        ''' Return object treeview icon. '''
        return str(os.path.join(DirIcons, "subplant.svg"))

    def claimChildren(self):
        """ Provides object grouping """
        children = []
        if self.Object.Frames:
            children.extend(self.Object.Frames)
        return children

    def __getstate__(self):
        return None

    '''def onDelete(self, feature, subelements):
        try:
            for obj in self.claimChildren():
                obj.ViewObject.show()
        except Exception as err:
            FreeCAD.Console.PrintError("Error in onDelete: " + str(err))
        return True

    def canDragObjects(self):
        return True

    def canDropObjects(self):
        return True

    def canDragObject(self, dragged_object):
        return True

    def canDropObject(self, incoming_object):
        return hasattr(incoming_object, 'Shape')

    def dragObject(self, selfvp, dragged_object):
        objs = self.Object.Objects
        objs.remove(dragged_object)
        self.Object.Objects = objs

    def dropObject(self, selfvp, incoming_object):
        self.Object.Objects = self.Object.Objects + [incoming_object]

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
        return None'''

# Comandos: -----------------------------------------------------------------------------------------------------------
class CommandDivideArea:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "area.svg")),
                'Accel': "A, D",
                'MenuText': "Divide Area",
                'ToolTip': "Allowed Area"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]


    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class CommandBoundary:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "area.svg")),
                'Accel': "A, B",
                'MenuText': "Area",
                'ToolTip': "Allowed Area"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        obj = makeArea([ver.Point for ver in sel.Shape.Vertexes])
        #taskd = _PVPlantPlacementTaskPanel()
        #FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


class CommandFrameArea:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "FrameArea.svg")),
                'Accel': "A, F",
                'MenuText': "Frame Area",
                'ToolTip': "Frame Area"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        makeFramedArea(sel[0])

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class CommandProhibitedArea:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "area_forbidden.svg")),
                'Accel': "A, F",
                'MenuText': "Prohibited Area",
                'ToolTip': "Prohibited Area"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        makeProhibitedArea(sel[0])

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class CommandPVSubplant:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "subplant.svg")),
                'Accel': "A, P",
                'MenuText': "PV Subplant",
                'ToolTip': "PV Subplant"}

    def Activated(self):
        area = makePVSubplant()
        sel = FreeCADGui.Selection.getSelection()
        for obj in sel:
            if obj.Name[:7] == "Tracker":
                frame_list = area.Frames
                frame_list.append(obj)
                area.Frames = frame_list


    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class CommandOffsetArea:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "offset.svg")),
                'Accel': "A, O",
                'MenuText': "OffsetArea",
                'ToolTip': "OffsetArea"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        base = None
        if sel:
            base = sel[0]
        obj = makeOffsetArea(base)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    class CommandAreaGroup:

        def GetCommands(self):
            return tuple([#'Area',
                          'FrameArea',
                          'ForbiddenArea',
                          'PVSubplant',
                          'OffsetArea'
                          ])

        def GetResources(self):
            return {'MenuText': 'Areas',
                    'ToolTip': 'Areas'
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None

    #FreeCADGui.addCommand('Area', CommandBoundary())
    FreeCADGui.addCommand('FrameArea', CommandFrameArea())
    FreeCADGui.addCommand('ForbiddenArea', CommandProhibitedArea())
    FreeCADGui.addCommand('PVSubplant', CommandPVSubplant())
    FreeCADGui.addCommand('OffsetArea', CommandOffsetArea())
    FreeCADGui.addCommand('PVPlantAreas', CommandAreaGroup())
