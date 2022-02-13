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

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import draftguitools.gui_trackers as DraftTrackers
    import draftguitools.gui_tool_utils as gui_tool_utils
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
import PVPlantResources
from PVPlantResources import DirIcons as DirIcons


def makeBuilding(name="Building"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Building")
    obj.Label = name
    _Building(obj)
    _ViewProviderBuilding(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class _Building(ArchComponent.Component):
    "A Building Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)

    def setProperties(self, obj):
        pl = obj.PropertiesList
        # Dimensions: --------------------------------------------------------------------------------------------------
        if not "Height" in pl:
            obj.addProperty("App::PropertyLength",
                            "Height",
                            "Building",
                            "The height of this object"
                            ).Height = 4000

        if not "Width" in pl:
            obj.addProperty("App::PropertyLength",
                            "Width",
                            "Building",
                            "The width of this object"
                            ).Width = 7000

        if not "Length" in pl:
            obj.addProperty("App::PropertyLength",
                            "Length",
                            "Building",
                            "The height of this object"
                            ).Length = 14000

        if not "RoofHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "RoofHeight",
                            "Building",
                            "The height of this object"
                            ).RoofHeight = 1500

        if not "RoofTop" in pl:
            obj.addProperty("App::PropertyPercent",
                            "RoofTop",
                            "Building",
                            "The height of this object"
                            ).RoofTop = 50

        # outputs:
        if not "InternalVolume" in pl:
            obj.addProperty("App::PropertyVolume",
                            "InternalVolume",
                            "Outputs",
                            "The height of this object"
                            )

        if not "ExternalVolume" in pl:
            obj.addProperty("App::PropertyVolume",
                            "ExternalVolume",
                            "Outputs",
                            "The height of this object"
                            )

        self.Type = "Building"
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and Arch wall properties."""
        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

    def execute(self, obj):
        w = obj.Width.Value
        w_med = w / 2
        l_med = obj.Length.Value / 2

        p1 = FreeCAD.Vector(-l_med, -w_med, 0)
        p2 = FreeCAD.Vector(-l_med,  w_med, 0)
        p3 = FreeCAD.Vector(-l_med,  w_med, obj.Height.Value)
        p4 = FreeCAD.Vector(-l_med,  w * (obj.RoofTop - 50) / 100, obj.Height.Value + obj.RoofHeight.Value)
        p5 = FreeCAD.Vector(-l_med, -w_med, obj.Height.Value)

        profile = Part.Face(Part.makePolygon([p1, p2, p3, p4, p5, p1, ]))
        ext_sol = profile.extrude(FreeCAD.Vector(obj.Length.Value, 0, 0))

        obj.Shape = ext_sol


class _ViewProviderBuilding(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "house.svg"))

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
            taskd = _BuildingTaskPanel(self.Object)
            taskd.obj = self.Object
            # taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

        return False


class _BuildingTaskPanel:
    def __init__(self, obj=None):
        self.new = False
        if obj is None:
            self.new = True
            obj = makeBuilding()

        self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantBuilding.ui")

        self.node = None
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.tracker = DraftTrackers.ghostTracker(obj)
        self.tracker.on()
        self.call = self.view.addEventCallback("SoEvent", self.action)

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """

        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()

        elif arg["Type"] == "SoLocation2Event":
            point, ctrlPoint, info = gui_tool_utils.getPoint(self, arg)
            if info:
                self.tracker.move(FreeCAD.Vector(info["x"], info["y"], info["z"]))
            else:
                self.tracker.move(point)

        elif (arg["Type"] == "SoMouseButtonEvent" and
              arg["State"] == "DOWN" and
              arg["Button"] == "BUTTON1"):

            point, ctrlPoint, info = gui_tool_utils.getPoint(self, arg)
            if info:
                self.obj.Placement.Base = FreeCAD.Vector(info["x"], info["y"], info["z"])
            else:
                self.obj.Placement.Base = point
            self.finish()

    def finish(self):
        self.accept()

    def accept(self):
        self.closeForm()
        return True

    def reject(self):
        if self.new:
            FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        self.closeForm()
        return True

    def closeForm(self):
        self.tracker.finalize()
        FreeCADGui.Control.closeDialog()
        self.view.removeEventCallback("SoEvent", self.call)


class _CommandBuilding:
    "the Arch Building command definition"
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "house.svg")),
                'MenuText': "Building",
                'Accel': "C, M",
                'ToolTip': "Creates a Building object from setup dialog."}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        TaskPanel = _BuildingTaskPanel()
        FreeCADGui.Control.showDialog(TaskPanel)
        return


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantBuilding', _CommandBuilding())
