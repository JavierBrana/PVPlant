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
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
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

from PVPlantResources import DirIcons as DirIcons


def makeTrace(points = None, label = "Trace"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Trace")
    obj.Label = label
    Trace(obj)
    ViewProviderTrace(obj.ViewObject)
    if points:
        obj.Points = points
    return obj


class Trace:
    def __init__(self, obj):
        self.setCommonProperties(obj)

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList
        if not ("Points" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "Points",
                            "PlacementLine",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        self.Type = "TraceLine"
        obj.Proxy = self

    def execute(self, obj):
        if len(obj.Points) > 1:
            obj.Shape = Part.makePolygon(obj.Points)


class ViewProviderTrace:
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

        return str(os.path.join(DirIcons, "Trace.svg"))

    def setEdit(self, vobj, mode=0):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard Point Edit task panel.

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

        # TODO: Cambiar esto para poder editar puntos
        if (mode == 0) and hasattr(self, "Object"):
            # taskd = _TrackerTaskPanel(self.Object)
            # taskd.obj = self.Object
            # FreeCADGui.Control.showDialog(taskd)
            return True

        return False

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