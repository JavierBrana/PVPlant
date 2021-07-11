import FreeCAD
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui, os
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
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    return obj

class _Cable(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setProperties(obj)
        self.Type = "Cable"

        self.route = None

        obj.Proxy = self
        obj.IfcType = "Cable Segment"
        obj.setEditorMode("IfcType", 1)

    def setProperties(self, obj):
        # Definicion de Propiedades:

        obj.addProperty("App::PropertyLink",
                        "From",
                        "Connections",
                        QT_TRANSLATE_NOOP("App::Property", "Connection "))

        obj.addProperty("App::PropertyLink",
                        "To",
                        "Connections",
                        QT_TRANSLATE_NOOP("App::Property", "Connection "))

        obj.addProperty("App::PropertyDistance",
                        "Distance",
                        "Cable",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Distance = 0
        obj.setEditorMode("Distance", 1)

        obj.addProperty("App::PropertyDistance",
                        "Diameter",
                        "Cable",
                        QT_TRANSLATE_NOOP("App::Property", "Diameter")).Diameter = 6.6

        obj.addProperty("App::PropertyArea",
                        "Seccion",
                        "Cable",
                        QT_TRANSLATE_NOOP("App::Property", "Sección"))

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.obj = obj
        self.Type = "Cable"
        obj.Proxy = self

    def __getstate__(self):
        return self.route

    def __setstate__(self, state):
        self.route = state

    def execute(self, obj):
        import Part, DraftGeomUtils, math
        import Draft

        if not obj.From or not obj.To:
            return

        w = None
        if self.route:
            # Si tiene ruta, dibujar ruteado
            print("Ruteado")


        else:
            line = Part.LineSegment()
            line.StartPoint = obj.From.Shape.Faces[4].CenterOfMass  # obj.From.Placement.Base
            line.EndPoint = obj.To.Shape.Faces[4].CenterOfMass  # obj.To.Placement.Base
            w = Part.Wire(line.toShape())

        p = Part.Wire([Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), obj.Diameter.Value / 2).toShape()])
        '''
        if obj.WallThickness.Value and (obj.WallThickness.Value < obj.Diameter.Value / 2):
            p2 = Part.Wire([Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1),
                                        (obj.Diameter.Value / 2 - obj.WallThickness.Value)).toShape()])
            p = Part.Face(p)
            p2 = Part.Face(p2)
            p = p.cut(p2)
        '''
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
                sh = w.makePipeShell([f.OuterWire],True,False,2)
                for shw in f.Wires:
                    if shw.hashCode() != f.OuterWire.hashCode():
                        sh2 = w.makePipeShell([shw],True,False,2)
                        sh = sh.cut(sh2)
                shapes.append(sh)
        elif p.Wires:
            for pw in p.Wires:
                sh = w.makePipeShell([pw],True,False,2)
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