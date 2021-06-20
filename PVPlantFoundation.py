# -*- coding: utf-8 -*-

# ***************************************************************************
# *   Copyright (c) 2016 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD, ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui, Arch_rc, os
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

## @package ArchFoundation
#  \ingroup ARCH
#  \brief The Foundation object and tools
#
#  This module provides tools to build Foundation and Foundation connector objects.
#  Foundations are tubular objects extruded along a base line.

__title__ = "Arch Foundation tools"
__author__ = "Yorik van Havre"
__url__ = "http://www.freecadweb.org"


def makeFoundation(baseobj=None, diameter=200, length=700, placement=None, name="Foundation"):
    "makeFoundation([baseobj,diamerter,length,placement,name]): creates an Foundation object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    obj.Label = name
    _PVPlantFoundation(obj)

    if FreeCAD.GuiUp:
        _ViewProviderFoundation(obj.ViewObject)
        if baseobj:
            baseobj.ViewObject.hide()
    if baseobj:
        obj.Base = baseobj
    else:
        if length:
            obj.Length = length
        else:
            obj.Length = 1000
    if diameter:
        obj.Diameter = diameter
    else:
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
        obj.Diameter = p.GetFloat("PipeDiameter", 50)
    if placement:
        obj.Placement = placement
    return obj


class _CommandFoundation:
    "the Arch Foundation command definition"

    def GetResources(self):

        return {'Pixmap': 'Foundation',
                'MenuText': QT_TRANSLATE_NOOP("Foundation", "Foundation"),
                'Accel': "P, I",
                'ToolTip': QT_TRANSLATE_NOOP("Foundation",
                                             "Creates a Foundation object from a given Wire or Line")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        '''
        FreeCAD.ActiveDocument.openTransaction(translate("Arch", "Create Foundation"))
        FreeCADGui.addModule("Arch")
        FreeCADGui.doCommand("obj = Arch.makeFoundation()")
        FreeCADGui.addModule("Draft")
        FreeCADGui.doCommand("Draft.autogroup(obj)")
        FreeCAD.ActiveDocument.commitTransaction()
        '''
        import Draft
        obj = makeFoundation()
        Draft.autogroup(obj)
        FreeCAD.ActiveDocument.recompute()


class _PVPlantFoundation(ArchComponent.Component):
    "the PVPlant Foundation object"

    def __init__(self, obj):

        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        obj.IfcType = "Element"

    def setProperties(self, obj):

        pl = obj.PropertiesList
        if not "Diameter" in pl:
            obj.addProperty("App::PropertyLength", "Diameter", "Foundation", QT_TRANSLATE_NOOP("App::Property",
                                                                                               "The diameter of this Foundation, if not based on a profile"))
        if not "Length" in pl:
            obj.addProperty("App::PropertyLength", "Length", "Foundation", QT_TRANSLATE_NOOP("App::Property",
                                                                                             "The length of this Foundation, if not based on an edge"))
        if not "Profile" in pl:
            obj.addProperty("App::PropertyLink", "Profile", "Foundation",
                            QT_TRANSLATE_NOOP("App::Property", "An optional closed profile to base this Foundation on"))

        self.Type = "Foundation"

    def onDocumentRestored(self, obj):

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def execute(self, obj):

        import Part, DraftGeomUtils, math
        pl = obj.Placement
        w = self.getWire(obj)
        if not w:
            FreeCAD.Console.PrintError(translate("Arch", "Unable to build the base path") + "\n")
            return

        p = self.getProfile(obj)
        if not p:
            FreeCAD.Console.PrintError(translate("Arch", "Unable to build the profile") + "\n")
            return

        # move and rotate the profile to the first point
        delta = w.Vertexes[0].Point - p.CenterOfMass
        p.translate(delta)
        import Draft
        if Draft.getType(obj.Base) == "BezCurve":
            v1 = obj.Base.Placement.multVec(obj.Base.Points[1]) - w.Vertexes[0].Point
        else:
            v1 = w.Vertexes[1].Point - w.Vertexes[0].Point
        v2 = DraftGeomUtils.getNormal(p)
        rot = FreeCAD.Rotation(v2, v1)
        p.rotate(p.CenterOfMass, rot.Axis, math.degrees(rot.Angle))

        try:
            sh = w.makePipeShell([p], True, False, 2)
        except:
            FreeCAD.Console.PrintError(translate("Arch", "Unable to build the Foundation -- ") + "\n")
        else:
            obj.Shape = sh
            if obj.Base:
                obj.Length = w.Length
            else:
                obj.Placement = pl

    def getWire(self, obj):

        import Part
        if obj.Base:
            if not hasattr(obj.Base, 'Shape'):
                FreeCAD.Console.PrintError(translate("Arch", "The base object is not a Part") + "\n")
                return
            if len(obj.Base.Shape.Wires) != 1:
                FreeCAD.Console.PrintError(translate("Arch", "Too many wires in the base shape") + "\n")
                return
            if obj.Base.Shape.Wires[0].isClosed():
                FreeCAD.Console.PrintError(translate("Arch", "The base wire is closed") + "\n")
                return
            w = obj.Base.Shape.Wires[0]
        else:
            if obj.Length.Value == 0:
                return
            w = Part.Wire([Part.LineSegment(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, obj.Length.Value)).toShape()])
        return w

    def getProfile(self, obj):

        import Part
        if obj.Profile:
            if not obj.Profile.getLinkedObject().isDerivedFrom("Part::Part2DObject"):
                FreeCAD.Console.PrintError(translate("Arch", "The profile is not a 2D Part") + "\n")
                return
            if len(obj.Profile.Shape.Wires) != 1:
                FreeCAD.Console.PrintError(translate("Arch", "Too many wires in the profile") + "\n")
                return
            if not obj.Profile.Shape.Wires[0].isClosed():
                FreeCAD.Console.PrintError(translate("Arch", "The profile is not closed") + "\n")
                return
            p = obj.Profile.Shape.Wires[0]
        else:
            if obj.Diameter.Value == 0:
                return
            p = Part.Wire(
                [Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), obj.Diameter.Value / 2).toShape()])
        return p


class _ViewProviderFoundation(ArchComponent.ViewProviderComponent):
    "A View Provider for the Foundation object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        import Arch_rc
        return ":/icons/Arch_Pipe_Tree.svg"


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantFoundation', _CommandFoundation())
