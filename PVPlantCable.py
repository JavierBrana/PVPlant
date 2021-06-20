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
        '''[
        'App::PropertyBool',
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
        'Mesh::PropertyNormalList',
        'Mesh::PropertyCurvatureList',
        'Mesh::PropertyMeshKernel',
        'Sketcher::PropertyConstraintList'
        ]'''

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








def makePipe(baseobj=None,diameter=0,length=0,placement=None,name="Pipe"):

    "makePipe([baseobj,diamerter,length,placement,name]): creates an pipe object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return
    obj= FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
    obj.Label = name
    _ArchPipe(obj)
    if FreeCAD.GuiUp:
        _ViewProviderPipe(obj.ViewObject)
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
        obj.Diameter = p.GetFloat("PipeDiameter",50)
    if placement:
        obj.Placement = placement
    return obj

class _ArchPipe(ArchComponent.Component):

    def __init__(self,obj):

        ArchComponent.Component.__init__(self,obj)
        self.setProperties(obj)
        # IfcPipeSegment is new in IFC4
        from ArchIFC import IfcTypes
        if "Pipe Segment" in IfcTypes:
            obj.IfcType = "Pipe Segment"
        else:
            # IFC2x3 does not know a Pipe Segment
            obj.IfcType = "Undefined"

    def setProperties(self,obj):

        pl = obj.PropertiesList
        if not "Diameter" in pl:
            obj.addProperty("App::PropertyLength", "Diameter",     "Pipe", QT_TRANSLATE_NOOP("App::Property","The diameter of this pipe, if not based on a profile"))
        if not "Length" in pl:
            obj.addProperty("App::PropertyLength", "Length",       "Pipe", QT_TRANSLATE_NOOP("App::Property","The length of this pipe, if not based on an edge"))
        if not "Profile" in pl:
            obj.addProperty("App::PropertyLink",   "Profile",      "Pipe", QT_TRANSLATE_NOOP("App::Property","An optional closed profile to base this pipe on"))
        if not "OffsetStart" in pl:
            obj.addProperty("App::PropertyLength", "OffsetStart",  "Pipe", QT_TRANSLATE_NOOP("App::Property","Offset from the start point"))
        if not "OffsetEnd" in pl:
            obj.addProperty("App::PropertyLength", "OffsetEnd",    "Pipe", QT_TRANSLATE_NOOP("App::Property","Offset from the end point"))
        if not "WallThickness" in pl:
            obj.addProperty("App::PropertyLength", "WallThickness","Pipe", QT_TRANSLATE_NOOP("App::Property","The wall thickness of this pipe, if not based on a profile"))
        self.Type = "Pipe"

    def onDocumentRestored(self,obj):

        ArchComponent.Component.onDocumentRestored(self,obj)
        self.setProperties(obj)

    def execute(self,obj):

        import Part,DraftGeomUtils,math
        pl = obj.Placement
        w = self.getWire(obj)
        if not w:
            FreeCAD.Console.PrintError(translate("Arch","Unable to build the base path")+"\n")
            return
        if obj.OffsetStart.Value:
            e = w.Edges[0]
            v = e.Vertexes[-1].Point.sub(e.Vertexes[0].Point).normalize()
            v.multiply(obj.OffsetStart.Value)
            e = Part.LineSegment(e.Vertexes[0].Point.add(v),e.Vertexes[-1].Point).toShape()
            w = Part.Wire([e]+w.Edges[1:])
        if obj.OffsetEnd.Value:
            e = w.Edges[-1]
            v = e.Vertexes[0].Point.sub(e.Vertexes[-1].Point).normalize()
            v.multiply(obj.OffsetEnd.Value)
            e = Part.LineSegment(e.Vertexes[-1].Point.add(v),e.Vertexes[0].Point).toShape()
            w = Part.Wire(w.Edges[:-1]+[e])
        p = self.getProfile(obj)
        if not p:
            FreeCAD.Console.PrintError(translate("Arch","Unable to build the profile")+"\n")
            return
        # move and rotate the profile to the first point
        if hasattr(p,"CenterOfMass"):
            c = p.CenterOfMass
        else:
            c = p.BoundBox.Center
        delta = w.Vertexes[0].Point - c
        p.translate(delta)
        import Draft
        if Draft.getType(obj.Base) == "BezCurve":
            v1 = obj.Base.Placement.multVec(obj.Base.Points[1])-w.Vertexes[0].Point
        else:
            v1 = w.Vertexes[1].Point-w.Vertexes[0].Point
        v2 = DraftGeomUtils.getNormal(p)
        rot = FreeCAD.Rotation(v2,v1)
        p.rotate(w.Vertexes[0].Point,rot.Axis,math.degrees(rot.Angle))
        shapes = []
        try:
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
        except Exception:
            FreeCAD.Console.PrintError(translate("Arch","Unable to build the pipe")+"\n")
        else:
            if len(shapes) == 0:
                return
            elif len(shapes) == 1:
                sh = shapes[0]
            else:
                sh = Part.makeCompound(shapes)
            obj.Shape = sh
            if obj.Base:
                obj.Length = w.Length
            else:
                obj.Placement = pl

    def getWire(self,obj):

        import Part
        if obj.Base:
            if not hasattr(obj.Base,'Shape'):
                FreeCAD.Console.PrintError(translate("Arch","The base object is not a Part")+"\n")
                return
            if len(obj.Base.Shape.Wires) != 1:
                FreeCAD.Console.PrintError(translate("Arch","Too many wires in the base shape")+"\n")
                return
            if obj.Base.Shape.Wires[0].isClosed():
                FreeCAD.Console.PrintError(translate("Arch","The base wire is closed")+"\n")
                return
            w = obj.Base.Shape.Wires[0]
        else:
            if obj.Length.Value == 0:
                return
            w = Part.Wire([Part.LineSegment(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,obj.Length.Value)).toShape()])
        return w

    def getProfile(self,obj):

        import Part
        if obj.Profile:
            if not obj.Profile.getLinkedObject().isDerivedFrom("Part::Part2DObject"):
                FreeCAD.Console.PrintError(translate("Arch","The profile is not a 2D Part")+"\n")
                return
            if not obj.Profile.Shape.Wires[0].isClosed():
                FreeCAD.Console.PrintError(translate("Arch","The profile is not closed")+"\n")
                return
            p = obj.Profile.Shape.Wires[0]
        else:
            if obj.Diameter.Value == 0:
                return
            p = Part.Wire([Part.Circle(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),obj.Diameter.Value/2).toShape()])
            if obj.WallThickness.Value and (obj.WallThickness.Value < obj.Diameter.Value/2):
                p2 = Part.Wire([Part.Circle(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),(obj.Diameter.Value/2-obj.WallThickness.Value)).toShape()])
                p = Part.Face(p)
                p2 = Part.Face(p2)
                p = p.cut(p2)
        return p


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