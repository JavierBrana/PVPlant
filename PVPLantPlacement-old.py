import FreeCAD
import ArchComponent
import Draft

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

import threading


def makePlacement(baseobj=None, diameter=0, length=0, placement=None, name="Placement"):
    "makePipe([baseobj,diamerter,length,placement,name]): creates an pipe object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    obj.Label = name
    _PVPlantPlacement(obj)

    if FreeCAD.GuiUp:
        _ViewProviderPVPlantPlacement(obj.ViewObject)
        if baseobj:
            baseobj.ViewObject.hide()

    return obj


class _CommandPVPlantPlacement:
    "the Arch Schedule command definition"

    def GetResources(self):
        return {'Pixmap': 'Placement',
                'Accel': "P, S",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        taskd = _PVPlantPlacementTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


class _PVPlantPlacement(ArchComponent.Component):
    "the PVPlantPlacement object"

    def __init__(self, obj):

        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        obj.MoveWithHost = False

    def setProperties(self, obj):
        ArchComponent.Component.setProperties(self, obj)

        pl = obj.PropertiesList

        if not "Section" in pl:
            obj.addProperty("App::PropertyLink", "Land", "Placement", QT_TRANSLATE_NOOP(
                "App::Property", "A single section of the fence"))

        if not "Post" in pl:
            obj.addProperty("App::PropertyLink", "Structure", "Placement", QT_TRANSLATE_NOOP(
                "App::Property", "A single fence post"))

        if not "Path" in pl:
            obj.addProperty("App::PropertyLink", "Path", "Placement", QT_TRANSLATE_NOOP(
                "App::Property", "The Path the fence should follow"))

        if not "NumberOfSections" in pl:
            obj.addProperty("App::PropertyInteger", "NumberOfSections", "Count", QT_TRANSLATE_NOOP(
                "App::Property", "The number of sections the fence is built of"))
            obj.setEditorMode("NumberOfSections", 1)

        if not "NumberOfPosts" in pl:
            obj.addProperty("App::PropertyInteger", "NumberOfPosts", "Count", QT_TRANSLATE_NOOP(
                "App::Property", "The number of posts used to build the fence"))
            obj.setEditorMode("NumberOfPosts", 1)

        self.Type = "Fence"

    def execute(self, obj):
        # fills columns A, B and C of the spreadsheet
        if not obj.Description:
            return

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


class _ViewProviderPVPlantPlacement:
    "A View Provider for PVPlantPlacement"

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        import Arch_rc
        return ":/icons/Arch_Schedule.svg"

    def attach(self, vobj):
        self.Object = vobj.Object

    def setEdit(self, vobj, mode):
        # taskd = _ArchScheduleTaskPanel(vobj.Object)
        # FreeCADGui.Control.showDialog(taskd)
        return True

    def doubleClicked(self, vobj):
        # taskd = _ArchScheduleTaskPanel(vobj.Object)
        # FreeCADGui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        # FreeCADGui.Control.closeDialog()
        return

    def claimChildren(self):
        # if hasattr(self,"Object"):
        #    return [self.Object.Result]
        return None

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def getDisplayModes(self, vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"

    def setDisplayMode(self, mode):
        return mode


class _PVPlantPlacementTaskPanel:
    '''The editmode TaskPanel for Schedules'''

    def __init__(self, obj=None):
        self.Terrain = None
        self.Rack = None
        self.Gap = 200
        self.Pitch = 4500

        # form:
        self.form = QtGui.QWidget()
        self.form.resize(800, 640)
        self.form.setWindowTitle("Curvas de nivel")
        self.form.setWindowIcon(QtGui.QIcon(":/icons/Arch_Schedule.svg"))
        self.grid = QtGui.QGridLayout(self.form)

        # parameters
        self.labelTerrain = QtGui.QLabel()
        self.labelTerrain.setText("Terreno:")
        self.lineTerrain = QtGui.QLineEdit(self.form)
        self.lineTerrain.setObjectName(_fromUtf8("lineTerrain"))
        self.lineTerrain.readOnly = True
        self.grid.addWidget(self.labelTerrain, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineTerrain, self.grid.rowCount() - 1, 1, 1, 1)
        self.buttonAddTerrain = QtGui.QPushButton('Sel')
        self.grid.addWidget(self.buttonAddTerrain, self.grid.rowCount() - 1, 2, 1, 1)

        self.labelRack = QtGui.QLabel()
        self.labelRack.setText("Rack:")
        self.lineRack = QtGui.QLineEdit(self.form)
        self.lineRack.setObjectName(_fromUtf8("lineRack"))
        self.lineRack.readOnly = True
        self.grid.addWidget(self.labelRack, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineRack, self.grid.rowCount() - 1, 1, 1, 1)
        self.buttonAddRack = QtGui.QPushButton('Sel')
        self.grid.addWidget(self.buttonAddRack, self.grid.rowCount() - 1, 2, 1, 1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        self.labelTypeStructure = QtGui.QLabel()
        self.labelTypeStructure.setText("Tipo de estructura:")
        self.valueTypeStructure = QtGui.QComboBox()
        self.valueTypeStructure.addItems(["Fixed", "Tracker 1 Axis"])
        self.valueTypeStructure.setCurrentIndex(0)
        self.grid.addWidget(self.labelTypeStructure, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueTypeStructure, self.grid.rowCount() - 1, 1, 1, -1)

        self.labelOrientation = QtGui.QLabel()
        self.labelOrientation.setText("Orientacion:")
        self.valueOrientation = QtGui.QComboBox()
        self.valueOrientation.addItems(["Norte-Sur", "Este-Oeste"])
        self.valueOrientation.setCurrentIndex(0)
        self.grid.addWidget(self.labelOrientation, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueOrientation, self.grid.rowCount() - 1, 1, 1, -1)

        self.labelGap = QtGui.QLabel()
        self.labelGap.setText("Espacio entre Columnas:")
        self.valueGap = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueGap.setText(str(self.Gap) + " mm")
        self.grid.addWidget(self.labelGap, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueGap, self.grid.rowCount() - 1, 1, 1, -1)

        self.labelPitch = QtGui.QLabel()
        self.labelPitch.setText("Separacion entre Filas:")
        self.valuePitch = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valuePitch.setText(str(self.Pitch) + " mm")
        self.grid.addWidget(self.labelPitch, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valuePitch, self.grid.rowCount() - 1, 1, 1, -1)

        self.labelAlign = QtGui.QLabel()
        self.labelAlign.setText("Método de alineación:")
        self.valueAlign = QtGui.QComboBox()
        self.valueAlign.addItems(["Si", "No"])
        self.valueAlign.setCurrentIndex(0)
        self.grid.addWidget(self.labelAlign, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueAlign, self.grid.rowCount() - 1, 1, 1, -1)

        self.line2 = QtGui.QFrame()
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line2, self.grid.rowCount(), 0, 1, -1)

        self.labelSideSlope = QtGui.QLabel()
        self.labelSideSlope.setText("Maxima inclinacion longitudinal:")
        self.valueSideSlope = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueSideSlope.setText("15")
        self.grid.addWidget(self.labelSideSlope, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueSideSlope, self.grid.rowCount() - 1, 1, 1, -1)

        QtCore.QObject.connect(self.buttonAddTerrain, QtCore.SIGNAL("clicked()"), self.addTerrain)
        QtCore.QObject.connect(self.buttonAddRack, QtCore.SIGNAL("clicked()"), self.addRack)
        # QtCore.QObject.connect(self.form.buttonDel, QtCore.SIGNAL("clicked()"), self.remove)
        # QtCore.QObject.connect(self.form.buttonClear, QtCore.SIGNAL("clicked()"), self.clear)
        # QtCore.QObject.connect(self.form.buttonSelect, QtCore.SIGNAL("clicked()"), self.select)

    def addTerrain(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.Terrain = sel[0]
            self.lineTerrain.setText(self.Terrain.Label)

    def addRack(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.Rack = sel[0]
            self.lineRack.setText(self.Rack.Label)

    def accept(self):
        if self.Terrain is not None and self.Rack is not None:
            self.Gap = FreeCAD.Units.Quantity(self.valueGap.text()).Value
            self.Pitch = FreeCAD.Units.Quantity(self.valuePitch.text()).Value
            self.placement()
        return True

    def placement(self):
        if self.valueTypeStructure.currentIndex() == 0:  # Fixed
            print("Rack")
        else:
            print("Tracker")
            if self.Rack.Height < self.Rack.Length:
                print("rotar")
                aux = self.Rack.Length
                self.Rack.Length = self.Rack.Height
                self.Rack.Height = aux

        self.Rack.Placement.Base.x = self.Terrain.Shape.BoundBox.XMin
        self.Rack.Placement.Base.y = self.Terrain.Shape.BoundBox.YMin

        DistColls = self.Rack.Length.Value + self.Gap
        DistRows = self.Rack.Height.Value + self.Pitch
        area = self.Rack.Shape.Faces[0].Area  # * 0.999999999

        import Draft
        rec = Draft.makeRectangle(length=self.Terrain.Shape.BoundBox.XLength, height=self.Rack.Height, face=True,
                                  support=None)
        rec.Placement.Base.x = self.Terrain.Shape.BoundBox.XMin
        rec.Placement.Base.y = self.Terrain.Shape.BoundBox.YMin

        try:
            while rec.Shape.BoundBox.YMax <= self.Terrain.Shape.BoundBox.YMax:
                common = self.Terrain.Shape.common(rec.Shape)
                for shape in common.Faces:
                    if shape.Area >= area:
                        if False:
                            minorPoint = FreeCAD.Vector(0, 0, 0)
                            for spoint in shape.OuterWire.Vertexes:
                                if minorPoint.y >= spoint.Point.y:
                                    if minorPoint.x >= spoint.x:
                                        minorPoint = spoint
                                        self.Rack.Placement.Base = spoint
                        else:
                            # más rápido
                            self.Rack.Placement.Base.x = shape.BoundBox.XMin
                            self.Rack.Placement.Base.y = shape.BoundBox.YMin

                        while self.Rack.Shape.BoundBox.XMax <= shape.BoundBox.XMax:
                            verts = [v.Point for v in rackClone.Shape.OuterWire.OrderedVertexes]
                            inside = True
                            for vert in verts:
                                if not shape.isInside(vert, 0, True):
                                    inside = False
                                    break

                            if inside:
                                raise
                            else:
                                # ajuste fino hasta encontrar el primer sitio:
                                rackClone.Placement.Base.x += 100  # un metro

                            '''old version
                            common1 = shape.common(self.Rack.Shape)
                            if common1.Area >= area:
                                raise
                            else:
                                # ajuste fino hasta encontrar el primer sitio:
                                self.Rack.Placement.Base.x += 500  # un metro
                            del common1
                            '''
                # ajuste fino hasta encontrar el primer sitio:
                rec.Placement.Base.y += 100
                del common
        except:
            pass
            #print("Found")

        FreeCAD.ActiveDocument.removeObject(rec.Name)

        from datetime import datetime
        starttime = datetime.now()

        if self.valueOrientation.currentIndex() == 0:
            # Código para crear filas:
            self.Rack.Placement.Base.x = self.Terrain.Shape.BoundBox.XMin
            i = 1
            yy = self.Rack.Placement.Base.y
            while yy < self.Terrain.Shape.BoundBox.YMax:
                CreateRow1(self.Rack.Placement.Base.x, yy, self.Rack, self.Terrain, DistColls, area, i)
                i += 1
                yy += DistRows
        elif self.valueOrientation.currentIndex() == 2:
            # Código para crear columnas:
            while self.Rack.Placement.Base.x > self.Terrain.Shape.BoundBox.XMin:
                self.Rack.Placement.Base.x -= DistColls
        else:
            xx = self.Rack.Placement.Base.x
            while xx < self.Terrain.Shape.BoundBox.XMax:
                CreateGrid(xx, self.Rack.Placement.Base.y, self.Rack, self.Terrain, DistRows, area)
                xx += DistColls

        FreeCAD.activeDocument().recompute()
        print("Everything OK (", datetime.now() - starttime, ")")


# Alinear solo filas. las columnas donde se pueda
def CreateRow(XX, YY, rack, land, gap, area, rowNumber):
    import Draft
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.format(a=rowNumber)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    rec = Draft.makeRectangle(length=land.Shape.BoundBox.XLength, height=rack.Height, face=True, support=None)
    rec.Placement.Base.x = land.Shape.BoundBox.XMin
    rec.Placement.Base.y = YY
    FreeCAD.activeDocument().recompute()

    common = land.Shape.common(rec.Shape)
    for shape in common.Faces:
        if shape.Area >= area:
            rackClone.Placement.Base.x = shape.BoundBox.XMin
            rackClone.Placement.Base.y = shape.BoundBox.YMin
            while rackClone.Shape.BoundBox.XMax <= shape.BoundBox.XMax:
                common1 = shape.common(rackClone.Shape)
                if common1.Area >= area:
                    tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height, placement=rackClone.Placement,
                                              face=True, support=None)
                    tmp.Label = 'R{:03}-000'.format(rowNumber)
                    rackClone.Placement.Base.x += gap
                else:
                    # ajuste fino hasta encontrar el primer sitio:
                    rackClone.Placement.Base.x += 500  # un metro
                del common1
    del common
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)
    FreeCAD.ActiveDocument.removeObject(rec.Name)


# Alinear solo filas. las columnas donde se pueda
def CreateRow1(XX, YY, rack, land, gap, area, rowNumber):
    import Draft
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.format(a=rowNumber)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    rec = Draft.makeRectangle(length=land.Shape.BoundBox.XLength, height=rack.Height, face=True, support=None)
    rec.Placement.Base.x = land.Shape.BoundBox.XMin
    rec.Placement.Base.y = YY
    FreeCAD.activeDocument().recompute()

    common = land.Shape.common(rec.Shape)
    for shape in common.Faces:
        if shape.Area >= area:
            if False:
                minorPoint = FreeCAD.Vector(0, 0, 0)
                for spoint in shape.OuterWire.Vertexes:
                    if minorPoint.y >= spoint.Point.y:
                        if minorPoint.x >= spoint.x:
                            minorPoint = spoint
                            rackClone.Placement.Base = spoint
            else:
                # más rápido
                rackClone.Placement.Base.x = shape.BoundBox.XMin
                rackClone.Placement.Base.y = shape.BoundBox.YMin

            while rackClone.Shape.BoundBox.XMax <= shape.BoundBox.XMax:
                verts = [v.Point for v in rackClone.Shape.OuterWire.OrderedVertexes]
                inside = True
                for vert in verts:
                    if not shape.isInside(vert, 0, True):
                        inside = False
                        break
                if inside:
                    #tmp = rack.Shape.copy()
                    #tmp.Placement = rack.Placement
                    tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height, placement=rackClone.Placement,
                                              face=True, support=None)
                    tmp.Label = 'R{:03}-000'.format(rowNumber)

                    rackClone.Placement.Base.x += gap
                else:
                    # ajuste fino hasta encontrar el primer sitio:
                    rackClone.Placement.Base.x += 500  # un metro
    del common
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)
    FreeCAD.ActiveDocument.removeObject(rec.Name)


# Alinear columna y fila (grid perfecta)
def CreateGrid(XX, YY, rack, land, gap, area):
    print("CreateGrid")
    import Draft
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.format(a=XX)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    # if False:
    while rackClone.Shape.BoundBox.YMax < land.Shape.BoundBox.YMax:
        common = land.Shape.common(rackClone.Shape)

        if common.Area >= area:
            tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height,
                                      placement=rackClone.Placement, face=True, support=None)
            tmp.Label = 'rackClone{a}'.format(a=XX)
        rackClone.Placement.Base.y += gap
        # else:
        #    # ajuste fino hasta encontrar el primer sitio:
        #    rackClone.Placement.Base.y += 1000
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)


# Alinear solo filas. las columnas donde se pueda
def CreateCol(XX, YY, rack, land, gap, area):
    import Draft
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.format(a=XX)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    while rackClone.Shape.BoundBox.YMax < land.Shape.BoundBox.YMax:
        common = land.Shape.common(rackClone.Shape)

        if common.Area >= area:
            tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height,
                                      placement=rackClone.Placement, face=True, support=None)
            tmp.Label = 'rackClone{a}'.format(a=XX)
            rackClone.Placement.Base.y += gap
        else:
            # ajuste fino hasta encontrar el primer sitio:
            rackClone.Placement.Base.y += 100

    FreeCAD.ActiveDocument.removeObject(rackClone.Name)


# TODO: Probar a usar hilos:
class _CreateCol(threading.Thread):
    def __init__(self, args=()):
        super().__init__()
        self.XX = args[0]
        self.YY = args[1]
        self.rack = args[2]
        self.land = args[3]
        self.gap = args[4]
        self.area = args[5]

    def run(self):
        import Draft
        # rackClone = Draft.makeRectangle(length=land.Shape.BoundBox.XLength, height=rack.Height,
        #                          face=True, support=None)
        # rackClone = FreeCAD.activeDocument().addObject('Part::Feature')
        # rackClone.Shape = self.rack.Shape

        rackClone = Draft.makeRectangle(length=self.rack.Length, height=self.rack.Height, face=True, support=None)
        rackClone.Label = 'rackClone{a}'.format(a=self.XX)
        rackClone.Placement.Base.x = self.XX
        rackClone.Placement.Base.y = self.YY

        # if False:
        while rackClone.Shape.BoundBox.YMax < self.land.Shape.BoundBox.YMax:
            common = self.land.Shape.common(rackClone.Shape)

            if common.Area >= self.area:
                rack = Draft.makeRectangle(length=self.rack.Length, height=self.rack.Height,
                                           placement=rackClone.Placement, face=True, support=None)
                rack.Label = 'rackClone{a}'.format(a=self.XX)
            rackClone.Placement.Base.y += self.gap
            # else:
            #    # ajuste fino hasta encontrar el primer sitio:
            #    rackClone.Placement.Base.y += 1000

        # FreeCAD.ActiveDocument.removeObject(rackClone.Name)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantPlacement', _CommandPVPlantPlacement())
