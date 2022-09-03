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

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import draftguitools.gui_trackers as DraftTrackers

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

__title__ = "Graph Terrain Profile"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"


def makeGraphProfile(path = None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "GraphProfile")
    _GraphProfile(obj)
    _ViewProviderGraphProfile(obj.ViewObject)

    if path:
        obj.Path = path

    return obj

class _GraphProfile:
    def __init__(self, obj):
        self.setCommonProperties(obj)

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("Path" in pl):
            obj.addProperty("App::PropertyLink",
                            "Path",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "")
                            )
            #obj.setEditorMode("NumberOfStrings", 1)

        if not ("AdjustToContent" in pl):
            obj.addProperty("App::PropertyBool",
                            "AdjustToContent",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "")
                            ).AdjustToContent = True

        if not ("PKMinorDistance" in pl):
            obj.addProperty("App::PropertyDistance",
                            "PKMinorDistance",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "")
                            ).PKMinorDistance = 20000

        if not ("YAxisStep" in pl):
            obj.addProperty("App::PropertyDistance",
                            "YAxisStep",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "")
                            ).YAxisStep = 5000

        if not ("Points" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "Points",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "")
                            )
            obj.setEditorMode("Points", 1)

        self.Type = "GraphProfile"
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''


        if prop == "Path":
            if obj.getPropertyByName(prop):
                from Utils import PVPlantUtils
                profile = PVPlantUtils.FlattenWire(PVPlantUtils.makeProfileFromTerrain(obj.Path))
                obj.Points = PVPlantUtils.getPointsFromVertexes(profile.Vertexes)
            else:
                obj.Points.clear()
        print("Graph: onChanged")

    def execute(self, obj):
        if (obj.Path is None) or (obj.Points is None):
            return

        profile = Part.makePolygon(obj.Points)
        xx_max = profile.BoundBox.XMax
        yy_min = profile.BoundBox.YMin
        yy_max = profile.BoundBox.YMax
        yy_length = yy_max
        yy_axis_minus = int(yy_min / 10) * 10 - obj.YAxisStep.Value

        # 1. Make Axis:
        x_axis = Part.makePolygon([FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(xx_max, 0, 0)])
        y_axis = None
        if obj.AdjustToContent:
            yy_length -= yy_min
            y_axis = Part.makePolygon([FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, (yy_max - yy_min) * 1.1, 0)])
            profile.Placement.Base.y = profile.Placement.Base.y - yy_min + obj.YAxisStep.Value
        else:
            y_axis = Part.makePolygon([FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, yy_max, 0)])

        shapes = []

        # 2. grid
        cnt = 0
        while cnt <= xx_max:
            line = y_axis.copy()
            line.Placement.Base = y_axis.Placement.Base + FreeCAD.Vector(cnt, 0, 0)
            shapes.append(line)
            cnt += obj.PKMinorDistance.Value

        cnt = 0
        while cnt <= yy_length:
            line = x_axis.copy()
            line.Placement.Base = x_axis.Placement.Base + FreeCAD.Vector(0, cnt, 0)
            shapes.append(line)
            cnt += obj.YAxisStep.Value

        shapes.append(profile)

        # Shape:
        obj.Shape = Part.makeCompound(shapes)



class _ViewProviderGraphProfile:
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

class _CommandGraphProfile:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "Profile.svg")),
                'Accel': "C, P",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Terrain Profile Graph"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "")}

    def Activated(self):
        path = None
        sel = FreeCADGui.Selection.getSelection()
        if len(sel)>0:
            path = sel[0]
        obj = makeGraphProfile(path)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('GraphTerrainProfile', _CommandGraphProfile())

