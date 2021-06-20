import FreeCAD
import Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
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

import os
from PVPlantResources import DirIcons as DirIcons


def SurfaceToPoints(suface):
    xmin = surface.BoundBox.XMin
    xmax = surface.BoundBox.XMax
    xlength = surface.BoundBox.XLenght
    ymin = surface.BoundBox.YMin
    ymax = surface.BoundBox.YMax
    ylength = surface.BoundBox.YLenght
    nondata = -999

    #x, y, z = [pt['geometry']['coordinates'] for pt in shape]
    #x, y , z = [pt.x, pt.y, pt.y for pt in surface.Mesh.Points]

    '''
    for point in surface.Mesh.Points:
        x = point.x
        y = point.y
        z = point.z
    '''

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    xi = np.linspace(min(x), max(x))
    yi = np.linspace(min(y), max(y))
    X, Y = np.meshgrid(xi, yi)

    Z = ml.griddata(x, y, z, xi, yi)


def Mest2FemMesh(obj):
    import Fem

    fm = Fem.FemMesh()

    #i = 0
    #nodes = []
    for mp in obj.Mesh.Points:
        fm.addNode(mp.Vector.x, mp.Vector.y, mp.Vector.z)
    #    nodes.append(mp)
    #    i += 1
    for mf in obj.Mesh.Facets:
        fm.addFace([mf.PointIndices[0] + 1, mf.PointIndices[1] + 1, mf.PointIndices[2] + 1])

    obj2 = FreeCAD.ActiveDocument.addObject("Fem::FemMeshObject")
    obj2.FemMesh = fm
    obj2.ViewObject.DisplayMode = "Faces"

    FreeCAD.activeDocument().recompute()
    return obj2

def Contours_Mesh(Mesh, minor = 1000, mayor = 5000,
                  minorColor=(0.0, 0.00, 0.80), mayorColor=(0.00, 0.00, 1.00),
                  minorLineWidth = 2, mayorLineWidth = 5,
                  filter_size = 5): #filter_size de 3 a 21 y siempre impar

    filter_radius = int(filter_size / 2)

    try:
        Contours = FreeCAD.ActiveDocument.Contours
    except:
        Contours = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Contours')

    if Mesh is not None:
        ZMin = Mesh.BoundBox.ZMin // 10000
        ZMin *= 10000
        ZMax = Mesh.BoundBox.ZMax

        inc = ZMin
        while inc < ZMax:
            CrossSections = Mesh.crossSections([((0, 0, inc), (0, 0, 1))], 0.000001)

            for PointList in CrossSections[0]:
                if len(PointList) > 1:
                    # 1. Smooth the points
                    if (len(PointList) > filter_size) and (filter_size > 0):
                        for a in range(len(PointList)):
                            x = 0
                            y = 0
                            for p in range(-filter_radius, filter_radius + 1):
                                point_id = a + p
                                if point_id < 0:
                                    point_id = 0

                                if point_id >= len(PointList):
                                    point_id = len(PointList) - 1

                                x += PointList[point_id].x
                                y += PointList[point_id].y

                            x /= filter_size
                            y /= filter_size
                            PointList[a].x = x
                            PointList[a].y = y

                        for a in reversed(range(len(PointList))):
                            x = 0
                            y = 0
                            for p in range(-filter_radius, filter_radius + 1):
                                point_id = a + p
                                if point_id < 0:
                                    point_id = 0

                                if point_id >= len(PointList):
                                    point_id = len(PointList) - 1

                                x += PointList[point_id].x
                                y += PointList[point_id].y

                            x /= filter_size
                            y /= filter_size
                            PointList[a].x = x
                            PointList[a].y = y

                    # 2. Make lines
                    Contour = Draft.makeWire(PointList, closed=False, face=None, support=None)
                    Contour.MakeFace = False
                    Contour.Label = str(int(inc / 1000)) + "m"
                    Contours.addObject(Contour)

                    if inc % mayor == 0:
                        Contour.ViewObject.LineWidth = mayorLineWidth
                        Contour.ViewObject.LineColor = mayorColor
                    else:
                        Contour.ViewObject.LineWidth = minorLineWidth
                        Contour.ViewObject.LineColor = minorColor

                    del Contour, PointList

            del CrossSections
            inc += minor

        FreeCAD.ActiveDocument.recompute()

def Contours_Part(Terrain, minor = 1000, mayor = 5000,
                  minorColor=(0.0, 0.00, 0.80), mayorColor=(0.00, 0.00, 1.00),
                  minorLineWidth = 2, mayorLineWidth = 5,
                  filter_size = 5): #filter_size de 3 a 21 y siempre impar

    filter_radius = int(filter_size / 2)

    try:
        Contours = FreeCAD.ActiveDocument.Contours
    except:
        Contours = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Contours')

    if Terrain is not None:
        ZMin = Terrain.Shape.BoundBox.ZMin // 10000
        ZMin *= 10000
        ZMax = Terrain.Shape.BoundBox.ZMax

        inc = ZMin
        while inc < ZMax:
            CrossSections = Terrain.Shape.slice(FreeCAD.Vector(0, 0, 1), inc)

            for wire in CrossSections:
                PointList = []
                for vertex in wire.Vertexes:
                    PointList.append(vertex.Point)

                if len(PointList) > 1:
                    # 1. Smooth the points
                    if (len(PointList) > filter_size) and (filter_size > 0):
                        for a in range(len(PointList)):
                            x = 0
                            y = 0
                            for p in range(-filter_radius, filter_radius + 1):
                                point_id = a + p
                                if point_id < 0:
                                    point_id = 0

                                if point_id >= len(PointList):
                                    point_id = len(PointList) - 1

                                x += PointList[point_id].x
                                y += PointList[point_id].y

                            x /= filter_size
                            y /= filter_size
                            PointList[a].x = x
                            PointList[a].y = y

                        for a in reversed(range(len(PointList))):
                            x = 0
                            y = 0
                            for p in range(-filter_radius, filter_radius + 1):
                                point_id = a + p
                                if point_id < 0:
                                    point_id = 0

                                if point_id >= len(PointList):
                                    point_id = len(PointList) - 1

                                x += PointList[point_id].x
                                y += PointList[point_id].y

                            x /= filter_size
                            y /= filter_size
                            PointList[a].x = x
                            PointList[a].y = y

                    # 2. Make lines
                    Contour = Draft.makeWire(PointList, closed=False, face=None, support=None)
                    Contour.MakeFace = False
                    Contour.Label = str(int(inc / 1000)) + "m"
                    Contours.addObject(Contour)

                    if inc % mayor == 0:
                        Contour.ViewObject.LineWidth = mayorLineWidth
                        Contour.ViewObject.LineColor = mayorColor
                    else:
                        Contour.ViewObject.LineWidth = minorLineWidth
                        Contour.ViewObject.LineColor = minorColor
            inc += minor


        FreeCAD.ActiveDocument.recompute()


# Contours Analisys: ---------------------------------------------------------------------------------
class _ContourTaskPanel:
    '''The editmode TaskPanel for contours generator'''

    def __init__(self):
        self.MinorColor = (0.5, 0.5, 0.5)
        self.MayorColor = (0.5, 0.5, 0.5)
        self.obj = None
        self.intervals = ["0.1 m", "0.5 m", "1 m", "5 m", "10 m", "50 m", "100 m", "500 m"]
        self.intervalvalues = [0.1, 0.5, 1, 5, 10, 50, 100, 500]

        # form:
        self.form = QtGui.QWidget()
        self.form.resize(800,640)
        self.form.setWindowTitle("Curvas de nivel")
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.form)

        # parameters
        self.labelTerrain = QtGui.QLabel()
        self.labelTerrain.setText("Terreno:")
        self.lineEdit1 = QtGui.QLineEdit(self.form)
        self.lineEdit1.setObjectName(_fromUtf8("lineEdit1"))
        self.lineEdit1.readOnly = True
        self.grid.addWidget(self.labelTerrain, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineEdit1, self.grid.rowCount() - 1, 1, 1, 1)

        self.buttonAdd = QtGui.QPushButton('Seleccionar Terreno')
        self.buttonAdd.clicked.connect(self.add)
        self.grid.addWidget(self.buttonAdd, self.grid.rowCount(), 1, 1, 1)

        ###----------------------

        self.widgetDivisions = QtGui.QGroupBox(self.form)
        self.grid.addWidget(self.widgetDivisions, self.grid.rowCount(), 0, 1, -1)
        self.gridDivisions = QtGui.QGridLayout(self.widgetDivisions)

        self.labelTitle1 = QtGui.QLabel()
        self.labelTitle1.setText("Intervalo")
        self.labelTitle2 = QtGui.QLabel()
        self.labelTitle2.setText("Grosor")
        self.labelTitle3 = QtGui.QLabel()
        self.labelTitle3.setText("Color")
        self.gridDivisions.addWidget(self.labelTitle1, self.gridDivisions.rowCount(), 1, 1, -1)
        self.gridDivisions.addWidget(self.labelTitle2, self.gridDivisions.rowCount() - 1, 2, 1, -1)
        self.gridDivisions.addWidget(self.labelTitle3, self.gridDivisions.rowCount() - 1, 3, 1, -1)

        self.labelMinorContour = QtGui.QLabel(self.form)
        self.labelMinorContour.setText("Menor:")
        self.inputMinorContourMargin = QtGui.QComboBox(self.form)
        self.inputMinorContourMargin.addItems(self.intervals)
        self.inputMinorContourMargin.setCurrentIndex(2)
        self.inputMinorContourThickness = QtGui.QSpinBox(self.form)
        self.inputMinorContourThickness.setRange(1, 10)
        self.inputMinorContourThickness.setValue(2)

        self.gridDivisions.addWidget(self.labelMinorContour, self.gridDivisions.rowCount(), 0, 1, 1)
        self.gridDivisions.addWidget(self.inputMinorContourMargin, self.gridDivisions.rowCount() - 1, 1, 1, 1)
        self.gridDivisions.addWidget(self.inputMinorContourThickness, self.gridDivisions.rowCount() - 1, 2, 1, 1)

        self.buttonMinorContourColor = QtGui.QPushButton('')
        self.color = QtGui.QColor(128, 128, 128)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(self.color)
        self.buttonMinorContourColor.setIcon(QtGui.QIcon(colorPix))
        self.buttonMinorContourColor.clicked.connect(lambda: self.selColor(self.buttonMinorContourColor))
        self.gridDivisions.addWidget(self.buttonMinorContourColor, self.gridDivisions.rowCount() - 1, 3, 1, 1)

        ###----------------------
        
        self.labelMayorContour = QtGui.QLabel(self.form)
        self.labelMayorContour.setText("Mayor:")

        self.inputMayorContourMargin = QtGui.QComboBox(self.form)
        self.inputMayorContourMargin.addItems(self.intervals)
        self.inputMayorContourMargin.setCurrentIndex(3)

        self.inputMayorContourThickness = QtGui.QSpinBox(self.form)
        self.inputMayorContourThickness.setRange(1, 10)
        self.inputMayorContourThickness.setValue(5)

        self.gridDivisions.addWidget(self.labelMayorContour, self.gridDivisions.rowCount(), 0, 1, 1)
        self.gridDivisions.addWidget(self.inputMayorContourMargin, self.gridDivisions.rowCount() - 1, 1, 1, 1)
        self.gridDivisions.addWidget(self.inputMayorContourThickness, self.gridDivisions.rowCount() - 1, 2, 1, 1)

        self.buttonMayorContourColor = QtGui.QPushButton('')
        self.color = QtGui.QColor(128, 128, 128)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(self.color)
        self.buttonMayorContourColor.setIcon(QtGui.QIcon(colorPix))
        self.buttonMayorContourColor.clicked.connect(lambda: self.selColor(self.buttonMayorContourColor))
        self.gridDivisions.addWidget(self.buttonMayorContourColor, self.gridDivisions.rowCount() - 1, 3, 1, 1)


    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.lineEdit1.setText(self.obj.Label)

    def selColor(self, button):
        color = QtGui.QColorDialog.getColor()
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        button.setIcon(QtGui.QIcon(colorPix))

        r = float(color.red()/255.0)
        g = float(color.green()/255.0)
        b = float(color.blue()/255.0)
        col = (r, g, b)

        if button is self.buttonMinorContourColor:
            self.MinorColor = col
        elif button is self.buttonMayorContourColor:
            self.MayorColor = col

    def accept(self):
        if self.obj is None:
            print("No hay objetos para procesar")
            return False
        else:
            minor = FreeCAD.Units.Quantity(self.inputMinorContourMargin.currentText()).Value
            mayor = FreeCAD.Units.Quantity(self.inputMayorContourMargin.currentText()).Value

            i = 0
            if i == 0:
                if self.obj.TypeId == 'Mesh::Feature':
                    Contours_Mesh(self.obj.Mesh, minor, mayor, self.MinorColor, self.MayorColor,
                          self.inputMinorContourThickness.value(), self.inputMayorContourThickness.value())
                else:
                    Contours_Part(self.obj, minor, mayor, self.MinorColor, self.MayorColor,
                              self.inputMinorContourThickness.value(), self.inputMayorContourThickness.value())


            elif i == 1:
                import multiprocessing
                p = multiprocessing.Process(target=Contours_Mesh,
                                            args=(self.obj.Mesh, minor, mayor,
                                                  self.MinorColor, self.MayorColor,
                                                  self.inputMinorContourThickness.value(),
                                                  self.inputMayorContourThickness.value(), ))
                p.start()
                p.join()

            else:
                import threading
                hilo = threading.Thread(target = Contours_Mesh,
                                        args = (self.obj.Mesh, minor, mayor,
                                                self.MinorColor, self.MayorColor,
                                                self.inputMinorContourThickness.value(),
                                                self.inputMayorContourThickness.value()))
                hilo.daemon = True
                hilo.start()

            return True


# Height Analisys: ---------------------------------------------------------------------------------
class _HeightTaskPanel:
    '''The TaskPanel for Slope setup'''

    def __init__(self):
        self.obj = None

        # form:
        self.form = QtGui.QWidget()
        self.form.resize(800,640)
        self.form.setWindowTitle("Curvas de nivel")
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.form)

        # parameters
        self.labelTerrain = QtGui.QLabel()
        self.labelTerrain.setText("Terreno:")
        self.lineEdit1 = QtGui.QLineEdit(self.form)
        self.lineEdit1.setObjectName(_fromUtf8("lineEdit1"))
        self.lineEdit1.readOnly = True
        self.grid.addWidget(self.labelTerrain, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineEdit1, self.grid.rowCount() - 1, 1, 1, 1)

        self.buttonAdd = QtGui.QPushButton('+')
        self.grid.addWidget(self.buttonAdd, self.grid.rowCount() - 1, 2, 1, 1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        # Divisiones ---------------------------------------------------
        self.labelDivision = QtGui.QLabel()
        self.labelDivision.setText("Divisiones:")
        self.grid.addWidget(self.labelDivision, self.grid.rowCount(), 0, 1, 1)
        self.lineEditDivisions = QtGui.QSpinBox()
        self.lineEditDivisions.setMinimum(3);
        self.lineEditDivisions.setMaximum(10);
        self.grid.addWidget(self.lineEditDivisions, self.grid.rowCount() - 1, 1, 1, -1)


        # Title labels ---------------------------------------------------
        self.widgetDivisions = QtGui.QGroupBox()
        self.grid.addWidget(self.widgetDivisions, self.grid.rowCount(), 0, 1, -1)
        self.gridDivisions = QtGui.QGridLayout(self.widgetDivisions)
        self.labelColor = QtGui.QLabel()
        self.labelColor.setText("Colores")
        self.gridDivisions.addWidget(self.labelColor, 0, 0, 1, -1)
        self.labelMax = QtGui.QLabel()
        self.labelMax.setText("Max.")
        self.gridDivisions.addWidget(self.labelMax, 0, 1, 1, -1)
        self.labelMin = QtGui.QLabel()
        self.labelMin.setText("Min.")
        self.gridDivisions.addWidget(self.labelMin, 0, 2, 1, -1)
        print("  ---- Rows: {a}".format(a=self.gridDivisions.rowCount()))


        # buttons add remove colors --------------------------------------------

        #QtCore.QObject.connect(self.buttonAdd, QtCore.SIGNAL("clicked()"), self.add)
        self.buttonAdd.clicked.connect(self.add)
        QtCore.QObject.connect(self.lineEditDivisions, QtCore.SIGNAL('valueChanged(int)'), self.addDivision)
        #self.lineEditDivisions.valueChanged.connect(self.addDivision)

    def addDivision(self):
        rows = self.gridDivisions.rowCount() - 1
        print(rows)

        if self.lineEditDivisions.value() > rows:
            for i in range(0, self.lineEditDivisions.value() - rows):
                self.createRow()
        elif self.lineEditDivisions.value() < rows:
            for i in range(0, rows - self.lineEditDivisions.value()):
                self.removeRow()

    def removeRow(self):
        row = self.gridDivisions.rowCount() - 1
        if row > 3:
            for col in range(self.gridDivisions.columnCount()):
                item = self.gridDivisions.itemAtPosition(row, col)
                if item is not None:
                    #item.widget().deleteLater()
                    self.gridDivisions.removeItem(item)
                    del item

    def createRow(self):
        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = QtGui.QColor(r, g, b)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        buttonColor = QtGui.QPushButton('')
        buttonColor.setIcon(QtGui.QIcon(colorPix))
        buttonColor.clicked.connect(lambda: self.selColor(buttonColor))
        self.gridDivisions.addWidget(buttonColor, self.gridDivisions.rowCount(), 0, 1, 1)

        max = QtGui.QSpinBox()
        max.setMinimum(0)
        max.setMaximum(100)
        self.gridDivisions.addWidget(max, self.gridDivisions.rowCount() - 1, 1, 1, 1)

        min = QtGui.QSpinBox()
        min.setMinimum(0)
        min.setMaximum(100)
        self.gridDivisions.addWidget(min, self.gridDivisions.rowCount() - 1, 2, 1, 1)

    def selColor(self, button):
        color = QtGui.QColorDialog.getColor()
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        button.setIcon(QtGui.QIcon(colorPix))

    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.lineEdit1.setText(self.obj.Label)

    def accept(self):
        if self.obj is None:
            print("No hay objetos para procesar")
            return False

        from datetime import datetime
        starttime = datetime.now()

        if self.obj.isDerivedFrom("Part::Feature"):
            escala = (self.obj.Shape.BoundBox.ZMax - self.obj.Shape.BoundBox.ZMin) / 100
            colorlist = []
            for face in self.obj.Shape.Faces:
                zz = (face.CenterOfMass.z - self.obj.Shape.BoundBox.ZMin) / escala

                if zz < 20:
                    colorlist.append((0.0, 1.0, 0.0))
                elif zz < 40:
                    colorlist.append((0.0, 1.0, 1.0))
                elif zz < 60:
                    colorlist.append((0.0, 0.0, 1.0))
                elif zz < 80:
                    colorlist.append((1.0, 0.0, 1.0))
                else:
                    colorlist.append((1.0, 0.0, 0.0))

            self.obj.ViewObject.DiffuseColor = colorlist

        elif obj.isDerivedFrom("Mesh::Feature"):
            fMesh = Mest2FemMesh(self.obj)
            escala = fMesh.FemMesh.BoundBox.ZMax - fMesh.FemMesh.BoundBox.ZMin

            import math
            colors={}
            if True:
                node = 1
                for point in self.obj.Mesh.Points:
                    zz = (point.Vector.z - self.obj.Mesh.BoundBox.ZMin) / escala * 100
                    # Cambiar esto a la lista de colores configurable
                    if zz < 20:
                        colors[node] = (0.0, 1.0, 0.0)
                    elif (zz < 40):
                        colors[node] = (0.0, 1.0, 1.0)
                    elif (zz < 60):
                        colors[node] = (0.0, 0.0, 1.0)
                    elif (zz < 80):
                        colors[node] = (1.0, 0.0, 1.0)
                    else:
                        colors[node] = (1.0, 0.0, 0.0)

                    node += 1

                #    (r, g, b, a) = cmap((point.Vector.z - self.obj.Mesh.BoundBox.ZMin) / escala)
                #    colors[node] = (r, g, b)
                #    node += 1
            else:
                # trabajar con FemMesh es desesperadamente lento:
                for node in fMesh.FemMesh.Nodes:
                    (r, g, b, a) = cmap((fMesh.FemMesh.Nodes[node].z - fMesh.FemMesh.BoundBox.ZMin)/escala)
                    colors[node] = (r, g, b)

            fMesh.ViewObject.NodeColor = colors

        FreeCAD.activeDocument().recompute()
        print("Orientation analisys OK (", datetime.now() - starttime, ")")
        return True


# Slope Analisys: ---------------------------------------------------------------------------------
class _SlopeTaskPanel:
    '''The TaskPanel for Slope setup'''

    def __init__(self):
        self.obj = None

        # form:
        self.form = QtGui.QWidget()
        self.form.resize(800, 640)
        self.form.setWindowTitle("Curvas de nivel")
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.form)

        # parameters
        self.labelTerrain = QtGui.QLabel()
        self.labelTerrain.setText("Terreno:")
        self.lineEdit1 = QtGui.QLineEdit(self.form)
        self.lineEdit1.setObjectName(_fromUtf8("lineEdit1"))
        self.lineEdit1.readOnly = True
        self.grid.addWidget(self.labelTerrain, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineEdit1, self.grid.rowCount() - 1, 1, 1, 1)

        self.buttonAdd = QtGui.QPushButton('+')
        self.grid.addWidget(self.buttonAdd, self.grid.rowCount() - 1, 2, 1, 1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        # Divisiones ---------------------------------------------------
        self.labelDivision = QtGui.QLabel()
        self.labelDivision.setText("Divisiones:")
        self.grid.addWidget(self.labelDivision, self.grid.rowCount(), 0, 1, 1)
        self.lineEditDivisions = QtGui.QSpinBox()
        self.lineEditDivisions.setMinimum(3)
        self.lineEditDivisions.setMaximum(10)
        self.grid.addWidget(self.lineEditDivisions, self.grid.rowCount() - 1, 1, 1, -1)

        # Title labels ---------------------------------------------------
        self.widgetDivisions = QtGui.QGroupBox()
        self.grid.addWidget(self.widgetDivisions, self.grid.rowCount(), 0, 1, -1)
        self.gridDivisions = QtGui.QGridLayout(self.widgetDivisions)
        self.labelColor = QtGui.QLabel()
        self.labelColor.setText("Colores")
        self.gridDivisions.addWidget(self.labelColor, 0, 0, 1, -1)
        self.labelMax = QtGui.QLabel()
        self.labelMax.setText("Max.")
        self.gridDivisions.addWidget(self.labelMax, 0, 1, 1, -1)
        self.labelMin = QtGui.QLabel()
        self.labelMin.setText("Min.")
        self.gridDivisions.addWidget(self.labelMin, 0, 2, 1, -1)

        self.tableWidget = QtGui.QTableWidget()
        self.grid.addWidget(self.tableWidget, self.grid.rowCount(), 0, 1, -1)

        self.tableWidget.verticalHeader().hide()
        #self.tableWidget.setShowGrid(False)
        #self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Ángulo min. (º)", "Ángulo máx. (º)", "Color"])


        for i in range(3):
            self.createRow()

        print("  ---- Rows: {a}".format(a=self.gridDivisions.rowCount()), "\n")

        # buttons add remove colors --------------------------------------------

        # QtCore.QObject.connect(self.buttonAdd, QtCore.SIGNAL("clicked()"), self.add)
        self.buttonAdd.clicked.connect(self.add)
        QtCore.QObject.connect(self.lineEditDivisions, QtCore.SIGNAL('valueChanged(int)'), self.changeDivision)
        # self.lineEditDivisions.valueChanged.connect(self.addDivision)

    def changeDivision(self):
        rows = self.tableWidget.rowCount()
        to = self.lineEditDivisions.value()

        maxval = float(self.tableWidget.item(self.tableWidget.rowCount() - 1, 1).text())

        if to > rows:
            for i in range(0, to - rows):
                self.createRow()
        elif to < rows:
            self.tableWidget.setRowCount(to)
            #for i in range(0, rows - to):
            #    self.removeRow()

        ran = maxval / self.tableWidget.rowCount()
        for i in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(i, 0)
            item.setText('{:.1f}'.format(ran *  i))
            item = self.tableWidget.item(i, 1)
            item.setText('{:.1f}'.format(ran *  (i + 1)))


        return
        rows = self.gridDivisions.rowCount() - 1
        print(rows)

        if self.lineEditDivisions.value() > rows:
            for i in range(0, self.lineEditDivisions.value() - rows):
                self.createRow()
        elif self.lineEditDivisions.value() < rows:
            for i in range(0, rows - self.lineEditDivisions.value()):
                self.removeRow()

    def removeRow(self):


        return
        row = self.gridDivisions.rowCount() - 1
        if row > 3:
            for col in range(self.gridDivisions.columnCount()):
                item = self.gridDivisions.itemAtPosition(row, col)
                if item is not None:
                    # item.widget().deleteLater()
                    self.gridDivisions.removeItem(item)
                    del item

    def createRow(self):
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

        newItem = QtGui.QTableWidgetItem("item")
        self.tableWidget.setItem(row, 0, newItem)
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        newItem.setText("0.0")

        newItem = QtGui.QTableWidgetItem("item")
        self.tableWidget.setItem(row, 1, newItem)
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        newItem.setText("0.0")

        '''
        comBox = QtGui.QComboBox()
        comBox.addItem("男")
        comBox.addItem("女")
        comBox.setStyleSheet("QComboBox{margin:3px};")
        tableWidget.setCellWidget(0, 1, comBox)
        '''

        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = QtGui.QColor(r, g, b)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        buttonColor = QtGui.QPushButton('')
        buttonColor.setIcon(QtGui.QIcon(colorPix))
        buttonColor.clicked.connect(lambda: self.selColor(buttonColor))
        '''
        searchBtn = QtGui.QPushButton("修改")
        searchBtn.setDown(True)
        searchBtn.setStyleSheet("QPushButton{margin:3px};")
        '''
        self.tableWidget.setCellWidget(row, 2, buttonColor)

        return
        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = QtGui.QColor(r, g, b)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        buttonColor = QtGui.QPushButton('')
        buttonColor.setIcon(QtGui.QIcon(colorPix))
        buttonColor.clicked.connect(lambda: self.selColor(buttonColor))
        self.gridDivisions.addWidget(buttonColor, self.gridDivisions.rowCount(), 0, 1, 1)

        max = QtGui.QSpinBox()
        max.setMinimum(0)
        max.setMaximum(100)
        self.gridDivisions.addWidget(max, self.gridDivisions.rowCount() - 1, 1, 1, 1)

        min = QtGui.QSpinBox()
        min.setMinimum(0)
        min.setMaximum(100)
        self.gridDivisions.addWidget(min, self.gridDivisions.rowCount() - 1, 2, 1, 1)

    def selColor(self, button):
        color = QtGui.QColorDialog.getColor()
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        button.setIcon(QtGui.QIcon(colorPix))

    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.lineEdit1.setText(self.obj.Label)
            print(self.obj.Label)

    def getFaceSlope(self, obj):
        import Mesh
        import math

        setColors = []
        for face in obj.Mesh.Facets:
            normal = face.Normal
            deg = normal.getAngle(FreeCAD.Vector(0, 0, 1))
            angle = math.degrees(deg)
            print(angle)
            # slope = math.tanh(deg)
            # print (slope)

    def getPointSlope(self):
        from datetime import datetime
        starttime = datetime.now()
        import math

        if self.obj.isDerivedFrom("Part::Feature"):
            colorlist = []

            # ejempo. Se sustituiría por una lista con la configuración real:
            rangos = [[0, 5, (0.0, 1.0, 0.0)],
                      [5, 7.5, (0.0, 0.8, 0.0)],
                      [7.5, 10, (0.0, 0.6, 0.0)],
                      [10, 12.5, (0.0, 0.5, 0.0)],
                      [12.5, 14, (1.0, 0.5, 0.0)],
                      [14, 20, (1.0, 0.0, 0.0)],
                      [20, 90, (0.6, 0.0, 0.0)]
                      ]

            for face in self.obj.Shape.Faces:
                normal = face.normalAt(0, 0)
                rad = normal.getAngle(FreeCAD.Vector(0, 0, 1))
                angle = math.degrees(rad)

                for rango in rangos:
                    if angle < rango[1]:
                        colorlist.append(rango[2])
                        break

            self.obj.ViewObject.DiffuseColor = colorlist

        elif obj.isDerivedFrom("Mesh::Feature"):
            fMesh = Mest2FemMesh(self.obj)

            import math
            setColors = []
            i = 1
            normals = self.obj.Mesh.getPointNormals()
            for normal in normals:
                rad = normal.getAngle(FreeCAD.Vector(0, 0, 1))
                angle = math.degrees(rad)

                # Cambiar esto a la lista de colores configurable
                if angle < 5:
                    setColors[i] = (0.0, 0.5, 0.0)
                elif angle < 7.5:
                    setColors[i] = (0.0, 1.0, 0.5)
                elif (angle < 10):
                    setColors[i] = (0.0, 1.0, 1.0)
                elif (angle < 12.5):
                    setColors[i] = (0.0, 0.0, 0.5)
                elif (angle < 14):
                    setColors[i] = (0.0, 0.0, 1.0)
                elif (angle > 20):
                    setColors[i] = (1.0, 0.0, 0.0)
                else:
                    setColors[i] = (1.0, 1.0, 1.0)
                i += 1

            fMesh.ViewObject.NodeColor = setColors

        FreeCAD.activeDocument().recompute()
        print("Everything OK (", datetime.now() - starttime, ")")

    def getPointsFromMesh(self):
        import csv
        import numpy as np
        import matplotlib.mlab as ml
        import scipy as sp
        import scipy.interpolate

        x = []
        y = []
        z = []
        for point in self.obj.Mesh.Points:
            x.append(point.x / 1000)
            y.append(point.y / 1000)
            z.append(point.z / 1000)

        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        spline = sp.interpolate.Rbf(x, y, z, function='thin-plate')
        return
        xi = np.linspace(min(x), max(x))
        yi = np.linspace(min(y), max(y))
        X, Y = np.meshgrid(xi, yi)
        Z = spline(X, Y)

        return

        print(X)
        xx = X.flatten()
        yy = Y.flatten()
        zz = Z.flatten()

        return xx, yy, zz
        '''
        i = 0
        pts = []
        for point in xx:
            pts.append(FreeCAD.Vector(xx[i] * 1000, yy[i] * 1000, zz[i] * 1000))
            i += 1

        PointObject.addPoints(pts)
        PointGroup.Points = PointObject
        '''

    def accept(self):
        print("Accept")
        if self.obj is None:
            print("No hay objetos para procesar")
            return False
        else:
            # self.getPointSlope()
            import threading
            hilo = threading.Thread(target=self.getPointSlope())
            hilo.start()
            return True

# Orientation Analisys: ---------------------------------------------------------------------------------
class _OrientationTaskPanel:
    '''The TaskPanel for Orientation setup'''

    def __init__(self):
        self.obj = None

        # form:
        self.form = QtGui.QWidget()
        self.form.resize(800,640)
        self.form.setWindowTitle("Curvas de nivel")
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.form)

        # parameters
        self.labelTerrain = QtGui.QLabel()
        self.labelTerrain.setText("Terreno:")
        self.lineEdit1 = QtGui.QLineEdit(self.form)
        self.lineEdit1.setObjectName(_fromUtf8("lineEdit1"))
        self.lineEdit1.readOnly = True
        self.grid.addWidget(self.labelTerrain, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.lineEdit1, self.grid.rowCount() - 1, 1, 1, 1)

        self.buttonAdd = QtGui.QPushButton('+')
        self.grid.addWidget(self.buttonAdd, self.grid.rowCount() - 1, 2, 1, 1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        # Divisiones ---------------------------------------------------
        self.labelDivision = QtGui.QLabel()
        self.labelDivision.setText("Divisiones:")
        self.grid.addWidget(self.labelDivision, self.grid.rowCount(), 0, 1, 1)
        self.lineEditDivisions = QtGui.QSpinBox()
        self.lineEditDivisions.setMinimum(3);
        self.lineEditDivisions.setMaximum(10);
        self.grid.addWidget(self.lineEditDivisions, self.grid.rowCount() - 1, 1, 1, -1)


        # Title labels ---------------------------------------------------
        self.widgetDivisions = QtGui.QGroupBox()
        self.grid.addWidget(self.widgetDivisions, self.grid.rowCount(), 0, 1, -1)
        self.gridDivisions = QtGui.QGridLayout(self.widgetDivisions)
        self.labelColor = QtGui.QLabel()
        self.labelColor.setText("Colores")
        self.gridDivisions.addWidget(self.labelColor, 0, 0, 1, -1)
        self.labelMax = QtGui.QLabel()
        self.labelMax.setText("Max.")
        self.gridDivisions.addWidget(self.labelMax, 0, 1, 1, -1)
        self.labelMin = QtGui.QLabel()
        self.labelMin.setText("Min.")
        self.gridDivisions.addWidget(self.labelMin, 0, 2, 1, -1)
        print("  ---- Rows: {a}".format(a=self.gridDivisions.rowCount()))


        # buttons add remove colors --------------------------------------------

        #QtCore.QObject.connect(self.buttonAdd, QtCore.SIGNAL("clicked()"), self.add)
        self.buttonAdd.clicked.connect(self.add)
        QtCore.QObject.connect(self.lineEditDivisions, QtCore.SIGNAL('valueChanged(int)'), self.addDivision)
        #self.lineEditDivisions.valueChanged.connect(self.addDivision)

    def addDivision(self):
        rows = self.gridDivisions.rowCount() - 1
        print(rows)

        if self.lineEditDivisions.value() > rows:
            for i in range(0, self.lineEditDivisions.value() - rows):
                self.createRow()
        elif self.lineEditDivisions.value() < rows:
            for i in range(0, rows - self.lineEditDivisions.value()):
                self.removeRow()

    def removeRow(self):
        row = self.gridDivisions.rowCount() - 1
        if row > 3:
            for col in range(self.gridDivisions.columnCount()):
                item = self.gridDivisions.itemAtPosition(row, col)
                if item is not None:
                    #item.widget().deleteLater()
                    self.gridDivisions.removeItem(item)
                    del item

    def createRow(self):
        import random
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = QtGui.QColor(r, g, b)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        buttonColor = QtGui.QPushButton('')
        buttonColor.setIcon(QtGui.QIcon(colorPix))
        buttonColor.clicked.connect(lambda: self.selColor(buttonColor))
        self.gridDivisions.addWidget(buttonColor, self.gridDivisions.rowCount(), 0, 1, 1)

        max = QtGui.QSpinBox()
        max.setMinimum(0)
        max.setMaximum(100)
        self.gridDivisions.addWidget(max, self.gridDivisions.rowCount() - 1, 1, 1, 1)

        min = QtGui.QSpinBox()
        min.setMinimum(0)
        min.setMaximum(100)
        self.gridDivisions.addWidget(min, self.gridDivisions.rowCount() - 1, 2, 1, 1)

    def selColor(self, button):
        color = QtGui.QColorDialog.getColor()
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        button.setIcon(QtGui.QIcon(colorPix))

    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.lineEdit1.setText(self.obj.Label)

    def accept(self):
        if self.obj is None:
            print("No hay objetos para procesar")
            return False

        from datetime import datetime
        import math
        starttime = datetime.now()

        if self.obj.isDerivedFrom("Part::Feature"):
            colorlist = []

            # ejempo. Se sustituiría por una lista con la configuración real:
            rangos = [[  0,  45, (0.0, 0.0, 0.0)],
                      [ 45,  90, (0.0, 0.0, 1.0)],
                      [ 90, 135, (0.0, 1.0, 0.0)],
                      [135, 180, (0.0, 1.0, 1.0)],
                      [180, 225, (1.0, 0.0, 0.0)],
                      [225, 270, (1.0, 0.0, 1.0)],
                      [270, 315, (1.0, 1.0, 0.0)],
                      [315, 360, (1.0, 1.0, 1.0)]
                     ]

            for face in self.obj.Shape.Faces:
                normal = face.normalAt(0, 0)
                normal.z = 0
                anglex = math.degrees(normal.getAngle(FreeCAD.Vector(1, 0, 0)))
                angley = math.degrees(normal.getAngle(FreeCAD.Vector(0, 1, 0)))
                if angley >= 90:
                    anglex = 360.0 - anglex

                anglex /= 2

                colorlist.append((0.0, 0.0, anglex / 360.0 + .5))
                continue

                for rango in rangos:
                    if anglex < rango[1]:
                        colorlist.append(rango[2])
                        break

                '''
                if anglex < 45:
                    colorlist.append((0.0, 0.0, 0.0))
                elif anglex < 90:
                    colorlist.append((0.0, 0.0, 1.0))
                elif anglex < 135:
                    colorlist.append((0.0, 1.0, 1.0))
                elif anglex < 180:
                    colorlist.append((1.0, 0.0, 0.0))
                elif anglex < 225:
                    colorlist.append((1.0, 0.0, 1.0))
                elif anglex < 270:
                    colorlist.append((1.0, 1.0, 0.0))
                elif anglex < 315:
                    colorlist.append((1.0, 1.0, 1.0))
                else:
                    colorlist.append((0.5, 0.5, 0.5))
                '''

            print(" Colores:\n", colorlist)
            self.obj.ViewObject.DiffuseColor = colorlist

        elif obj.isDerivedFrom("Mesh::Feature"):
            fMesh = Mest2FemMesh(self.obj)
            import Mesh
            fMesh = Mest2FemMesh(self.obj)

            setColors = {}
            i = 1
            normals = self.obj.Mesh.getPointNormals()
            print("   ---------   time to FEMMESH:  (", datetime.now() - starttime, ")")

            for normal in normals:
                rad = normal.getAngle(FreeCAD.Vector(1, 1, 0))
                angle = math.degrees(rad)

                # Cambiar esto a la lista de colores configurable
                if angle < 45:
                    setColors[i] = (0.0, 1.0, 0.0)
                elif (angle < 90):
                    setColors[i] = (0.0, 1.0, 1.0)
                elif (angle < 135):
                    setColors[i] = (0.0, 0.0, 1.0)
                elif (angle <= 180):
                    setColors[i] = (1.0, 0.0, 1.0)
                #else:
                #    setColors[i] = (1.0, 0.0, 0.0)

                i += 1
                if i== 1000:
                    break

            fMesh.ViewObject.NodeColor = setColors

        FreeCAD.activeDocument().recompute()
        print("Everything OK (", datetime.now() - starttime, ")")
        return True



## Comandos ----------------------------------------------------------------------------------------------------------
## 1. Contornos:
class _CommandContours:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "TerrainContours.svg")),
                'Accel': "T, C",
                'MenuText': 'Curvas de nivel',
                'ToolTip': 'Curvas de nivel'
                }

    def IsActive(self):
        # return not FreeCAD.ActiveDocument is None
        if FreeCAD.ActiveDocument is None:
            return False

        return True

        if FreeCADGui.Selection.getSelection() is not None:
            selection = FreeCADGui.Selection.getSelection()[-1]
            if selection.TypeId == 'Mesh::Feature':
                return True

        return False

    def Activated(self):
        self.TaskPanel = _ContourTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)

## 2. Aspect:
class _CommandSlopeAnalisys:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "TerrainSlope.svg")),
                'Accel': "T, S",
                'MenuText': 'Analisis de Pendiente',
                'ToolTip': 'Analisis de Pendiente'
                }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _SlopeTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)

## 3. Altura:
class _CommandHeightAnalisys:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "TerrainHeight.svg")),
                'Accel': "T, H",
                'MenuText': 'Analisis de Altura',
                'ToolTip': 'Analisis de Altura'
                }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _HeightTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)

## 4. Orientation:
class _CommandOrientationAnalisys:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "TerrainOrientation.svg")),
                'Accel': "T, H",
                'MenuText': 'Analisis de Orientación',
			    'ToolTip': 'Analisis de Orientación'
                }

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _OrientationTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)


# 5. Unión
if FreeCAD.GuiUp:
    class CommandTerrainAnalisysGroup:

        def GetCommands(self):
            return tuple(['Contours',
                          'HeightAnalisys',
                          'SlopeAnalisys',
                          'OrientationAnalisys'
                          ])
        def GetResources(self):
            return { 'MenuText': QT_TRANSLATE_NOOP("",'Terrain Analisys'),
                     'ToolTip': QT_TRANSLATE_NOOP("",'Terrain Analisys')
                   }
        def IsActive(self):
            return not FreeCAD.ActiveDocument is None

    FreeCADGui.addCommand('Contours', _CommandContours())
    FreeCADGui.addCommand('SlopeAnalisys', _CommandSlopeAnalisys())
    FreeCADGui.addCommand('HeightAnalisys', _CommandHeightAnalisys())
    FreeCADGui.addCommand('OrientationAnalisys', _CommandOrientationAnalisys())
    FreeCADGui.addCommand('TerrainAnalisys', CommandTerrainAnalisysGroup())