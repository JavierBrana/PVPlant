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
import Draft
import Part

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
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "PVArea")
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
        self.setCommonProperties(obj)

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("Points" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "Points",
                            "Area",
                            "Points that define the area"
                            )

        self.Type = "Area"
        obj.Proxy = self

    def execute(self, obj):
        if len(obj.Points) > 1:
            obj.Shape = Part.makePolygon(obj.Points)
        else:
            obj.Shape = Part.Shape()

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


''' Forbidden Area: '''


class _ProhibitedArea:
    def __init__(self, obj):
        self.setCommonProperties(obj)

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("Points" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "Points",
                            "Area",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        self.Type = "Area"
        obj.Proxy = self

    def execute(self, obj):
        if len(obj.Points) > 1:
            obj.Shape = Part.makePolygon(obj.Points)
        else:
            obj.Shape = Part.Shape()

class _ViewProviderForbiddenArea:
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

        return str(os.path.join(DirIcons, "area_forbidden.svg"))
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


''' PV Area: '''


def makePVArea():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "PVArea")
    _PVArea(obj)
    _ViewProviderPVArea(obj.ViewObject)
    return obj

class _PVArea(_Area):

    def __init__(self, obj):
        _Area.__init__(self, obj)
        self.setCommonProperties(obj)
        self.obj = obj

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("Frames" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Frames",
                            "PVArea",
                            "List of frames"
                            )

        if not ("Inverters" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Inverters",
                            "PVArea",
                            "List of Inverters"
                            )

        if not ("StringBoxes" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "StringBoxes",
                            "PVArea",
                            "List of String-Boxes"
                            )
        if not ("Cables" in pl):
            obj.addProperty("App::PropertyLinkList",
                            "Cables",
                            "PVArea",
                            "List of Cables"
                            )

        self.Type = "PVArea"
        obj.Proxy = self

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

    def onDocumentRestored(self, obj):
        """Method run when the document is restored."""

        self.setProperties(obj)

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

    def execute(self, obj):
        ''''''
        _Area.execute(self, obj)


class _ViewProviderPVArea:
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

    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None


# Comando: -----------------------------------------------------------------------------------------------------------

class _CommandBoundary:

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


class _CommandProhibitedArea:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "area_forbidden.svg")),
                'Accel': "A, B",
                'MenuText': "Prohibited Area",
                'ToolTip': "Prohibited Area"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        wire = None
        '''
        if sel:
            for obj in sel:
                if
        '''

        taskd = _PVPlantPlacementTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


class _CommandPVArea:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "A, P",
                'MenuText': "PVArea",
                'ToolTip': "PVArea"}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()[0]
        obj = makePVArea([ver.Point for ver in sel.Shape.Vertexes])

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


if FreeCAD.GuiUp:
    class CommandRackGroup:

        def GetCommands(self):
            return tuple(['Area',
                          'ForbiddenArea',
                          'PVArea'
                          ])

        def GetResources(self):
            return {'MenuText': QT_TRANSLATE_NOOP("", 'Areas'),
                    'ToolTip': QT_TRANSLATE_NOOP("", 'Areas')
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None

    FreeCADGui.addCommand('Area', _CommandBoundary())
    FreeCADGui.addCommand('ForbiddenArea', _CommandProhibitedArea())
    FreeCADGui.addCommand('PVArea', _CommandPVArea())
    FreeCADGui.addCommand('PVPlantAreas', CommandRackGroup())
