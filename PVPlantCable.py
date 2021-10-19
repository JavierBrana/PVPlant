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

if FreeCAD.GuiUp:
    import FreeCADGui, os
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

import PVPlantResources


def makeCable():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Cable")
    _Cable(obj)
    _ViewProviderCable(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    #FreeCADGui.ActiveDocument.ActiveView.fitAll()
    return obj


class _Cable(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        self.route = None

        obj.Proxy = self
        obj.IfcType = "Cable Segment"
        obj.setEditorMode("IfcType", 1)

    def setProperties(self, obj):

        pl = obj.PropertiesList
        if not ("From" in pl):
            obj.addProperty("App::PropertyLink",
                            "From",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "Connection "))

        if not ("To" in pl):
            obj.addProperty("App::PropertyLink",
                            "To",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "Connection "))


        if not ("Distance" in pl):
            obj.addProperty("App::PropertyDistance",
                            "Distance",
                            "Cable",
                            QT_TRANSLATE_NOOP("App::Property", "Connection")).Distance = 0
            obj.setEditorMode("Distance", 1)

        if not ("ExternalDiameter" in pl):
            obj.addProperty("App::PropertyDistance",
                            "ExternalDiameter",
                            "Cable",
                            QT_TRANSLATE_NOOP("App::Property", "Diameter")).ExternalDiameter = 6.6

        if not ("Section" in pl):
            obj.addProperty("App::PropertyArea",
                            "Section",
                            "Cable",
                            QT_TRANSLATE_NOOP("App::Property", "Sección"))
        self.Type = "Cable"

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)
        obj.Proxy = self

    def __getstate__(self):
        return self.route

    def __setstate__(self, state):
        self.route = state

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

    def execute(self, obj):
        import Part, DraftGeomUtils, math
        import Draft

        def getPoint(val):
            if val.Proxy.Type == 'String':
                return val.StringPoles[0]

            elif val.Proxy.Type == 'StringBox':
                #return val.PositiveIn1.CenterOfMass
                input = val.Shape.SubShapes[2].SubShapes[0]
                return input.CenterOfMass

            else:
                val.Shape.Faces[0].CenterOfMass

        if not obj.From or not obj.To:
            return

        w = None
        if self.route:
            # Si tiene ruta, dibujar ruteado
            print("Ruteado")
            w = self.route


        else:
            line = Part.LineSegment()
            line.StartPoint = getPoint(obj.From)
            line.EndPoint = getPoint(obj.To)
            w = Part.Wire(line.toShape())

        p = Part.Wire([Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), obj.ExternalDiameter.Value / 2).toShape()])

        if hasattr(p, "CenterOfMass"):
            c = p.CenterOfMass
        else:
            c = p.BoundBox.Center
        delta = w.Vertexes[0].Point - c
        p.translate(delta)
        if Draft.getType(obj.Base) == "BezCurve":
            v1 = obj.Base.Placement.multVec(obj.Base.Points[1]) - w.Vertexes[0].Point
        else:
            v1 = w.Vertexes[1].Point - w.Vertexes[0].Point
        v2 = DraftGeomUtils.getNormal(p)
        rot = FreeCAD.Rotation(v2, v1)
        p.rotate(w.Vertexes[0].Point, rot.Axis, math.degrees(rot.Angle))

        shapes = []
        if p.Faces:
            for f in p.Faces:
                sh = w.makePipeShell([f.OuterWire], True, False, 2)
                for shw in f.Wires:
                    if shw.hashCode() != f.OuterWire.hashCode():
                        sh2 = w.makePipeShell([shw], True, False, 2)
                        sh = sh.cut(sh2)
                shapes.append(sh)
        elif p.Wires:
            for pw in p.Wires:
                sh = w.makePipeShell([pw], True, False, 2)
                shapes.append(sh)

        obj.Shape = Part.makeCompound(shapes)
        d = 0
        obj.Distance = line.length()


class _ViewProviderCable(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "cable.png"))


class _CommandCable:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "cable.png")),
                'Accel': "E, C",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Cable"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Calcular el BOQ de la")}

    def Activated(self):
        makeCable()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantCable', _CommandCable())
