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

def makeContours(land, minor = 1000, mayor = 5000,
                 minorColor=(0.0, 0.00, 0.80), mayorColor=(0.00, 0.00, 1.00),
                 minorThickness = 2, mayorThickness = 5,
                 filter_size = 5):
    if not land:
        return

    if land.TypeId == 'Mesh::Feature':
        Contours_Mesh(land.Mesh, minor, mayor, minorColor, mayorColor, minorThickness, mayorThickness, filter_size)
    else:
        Contours_Part(land, minor, mayor, minorColor, mayorColor, minorThickness, mayorThickness, filter_size)

    FreeCAD.ActiveDocument.recompute()

def Contours_Mesh(Mesh, minor, mayor,
                  minorColor, mayorColor,
                  minorLineWidth, mayorLineWidth,
                  filter_size): #filter_size de 3 a 21 y siempre impar

    def calculateSection(cuts):
        for inc in cuts:
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

    filter_radius = int(filter_size / 2)
    try:
        Contours = FreeCAD.ActiveDocument.Contours
    except:
        Contours = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Contours')

    ZMin = Mesh.BoundBox.ZMin // 10000
    ZMin *= 10000
    ZMax = Mesh.BoundBox.ZMax

    import numpy as np
    minor_array = np.arange(ZMin, ZMax, minor)
    mayor_array = np.arange(ZMin, ZMax, mayor)
    minor_array = np.array(list(filter(lambda x: x not in mayor_array, minor_array)))
    calculateSection(minor_array)
    calculateSection(mayor_array)

def Contours_Part(Terrain, minor, mayor,
                  minorColor, mayorColor,
                  minorLineWidth, mayorLineWidth,
                  filter_size): #filter_size de 3 a 21 y siempre impar

    def calculateSection(cuts):
        cnt = 0
        for inc in cuts:
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
                    # 2. TODO: close wire

                    # 3. Make lines
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
            cnt += 1
            if cnt == 10:
                return

    filter_radius = int(filter_size / 2)
    try:
        Contours = FreeCAD.ActiveDocument.Contours
    except:
        Contours = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Contours')

    ZMin = Terrain.Shape.BoundBox.ZMin // 10000
    ZMin *= 10000
    ZMax = Terrain.Shape.BoundBox.ZMax

    import numpy as np
    minor_array = np.arange(ZMin, ZMax, minor)
    mayor_array = np.arange(ZMin, ZMax, mayor)
    minor_array = np.array(list(filter(lambda x: x not in mayor_array, minor_array)))
    calculateSection(minor_array)
    calculateSection(mayor_array)

# Base widget for task panel terrain analisys
class _generalTaskPanel:
    '''The TaskPanel for Slope setup'''

    def __init__(self):
        self.ranges = []

        self.form = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/PVPlantTerrainAnalisys.ui")
        self.tableWidget = self.form.tableWidget
        self.form.editSteps.valueChanged.connect(self.changeDivision)
        self.tableWidget.itemChanged.connect(self.cellChanged)

    def cellChanged(self, item):
        if (item.column() == 1) and (item.row() != (self.tableWidget.rowCount() - 1)):
            item2 = self.tableWidget.item(item.row() + 1, 0)
            item2.setText(item.text())

    def updateTableValues(self):
        maxval = self.form.editTo.value() - self.form.editFrom.value()
        ran = maxval / self.tableWidget.rowCount()

        for i in range(self.tableWidget.rowCount()):
            for j in range(2):
                item = self.tableWidget.item(i, j)
                val = ran * (i + j) + self.form.editFrom.value()
                item.setText('{:.1f}'.format(val))
                self.ranges[i][j] = val

        #self.tableWidget.item(0, 0).setText('{:.1f}'.format(self.form.editFrom.value()))
        #self.tableWidget.item(self.tableWidget.rowCount() - 1, 1).setText('{:.1f}'.format(self.form.editTo.value()))

    def changeDivision(self):
        self.tableWidget.blockSignals(True)
        rows = self.tableWidget.rowCount()
        to = self.form.editSteps.value()
        if to > rows:
            for i in range(0, to - rows):
                self.ranges.append([0.0, 0.0, (0.0, 0.0, 0.0)])
                self.createRow()
        elif to < rows:
            self.tableWidget.setRowCount(to)
            self.ranges = self.ranges[:to]
        self.updateTableValues()
        self.tableWidget.blockSignals(False)

    def createRow(self):
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

        newItem = QtGui.QTableWidgetItem("item")
        self.tableWidget.setItem(row, 0, newItem)
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        newItem.setText("0.0")
        newItem.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|
                         QtCore.Qt.ItemIsDropEnabled|QtCore.Qt.ItemIsUserCheckable)

        newItem = QtGui.QTableWidgetItem("item")
        self.tableWidget.setItem(row, 1, newItem)
        newItem.setTextAlignment(QtCore.Qt.AlignCenter)
        newItem.setText("0.0")

        #import random
        # r = random.randint(0, 255)
        # g = random.randint(0, 255)
        # b = random.randint(0, 255)

        val = int(127 * row / (self.form.editSteps.value() / 2))
        g = (127 + val) if val <= 127 else 0
        r = (328 - val if val >= 127 else 0)
        color = QtGui.QColor(r, g, 0)
        colorPix = QtGui.QPixmap(16, 16)
        colorPix.fill(color)
        self.ranges[row][2] = (color.red()/255, color.green()/255, color.blue()/255)
        buttonColor = QtGui.QPushButton('')
        buttonColor.setIcon(QtGui.QIcon(colorPix))
        buttonColor.setMaximumSize(QtCore.QSize(20, 20))
        buttonColor.clicked.connect(lambda: self.selColor(buttonColor))
        self.tableWidget.setCellWidget(row, 2, buttonColor)

    def selColor(self, button):
        color = QtGui.QColorDialog.getColor()
        if color.isValid():
            print("añadir color")
            colorPix = QtGui.QPixmap(16, 16)
            colorPix.fill(color)
            button.setIcon(QtGui.QIcon(colorPix))
            curentIndex = self.tableWidget.currentIndex()
            self.ranges[curentIndex.row()][2] = (color.red()/255, color.green()/255, color.blue()/255)

# Contours Analisys: ---------------------------------------------------------------------------------
class _ContourTaskPanel():
    '''The editmode TaskPanel for contours generator'''

    def __init__(self):
        self.MinorColor = (0.5, 0.5, 0.5)
        self.MayorColor = (0.5, 0.5, 0.5)
        land = None
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
            self.land = sel[0]
            self.lineEdit1.setText(self.land.Label)

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
        from datetime import datetime
        starttime = datetime.now()

        if self.land is None:
            print("No hay objetos para procesar")
            return False
        else:
            minor = FreeCAD.Units.Quantity(self.inputMinorContourMargin.currentText()).Value
            mayor = FreeCAD.Units.Quantity(self.inputMayorContourMargin.currentText()).Value

            i = 2
            if i == 0:
                makeContours(self.land, minor, mayor, self.MinorColor, self.MayorColor,
                          self.inputMinorContourThickness.value(), self.inputMayorContourThickness.value())
            elif i == 1:
                import multiprocessing
                p = multiprocessing.Process(target=makeContours,
                                            args=(self.land, minor, mayor,
                                                  self.MinorColor, self.MayorColor,
                                                  self.inputMinorContourThickness.value(),
                                                  self.inputMayorContourThickness.value(), ))
                p.start()
                p.join()

            else:
                import threading
                hilo = threading.Thread(target = makeContours,
                                        args = (self.land, minor, mayor,
                                                self.MinorColor, self.MayorColor,
                                                self.inputMinorContourThickness.value(),
                                                self.inputMayorContourThickness.value()))
                hilo.daemon = True
                hilo.start()

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        FreeCADGui.Control.closeDialog()
        return True

# Height Analisys: ---------------------------------------------------------------------------------
class _HeightTaskPanel(_generalTaskPanel):
    '''The TaskPanel for Slope setup'''

    def __init__(self):
        _generalTaskPanel.__init__(self)

        # Initial set-up:
        land = FreeCAD.ActiveDocument.Site.Terrain
        self.form.editFrom.setSuffix(" m")
        self.form.editFrom.setValue(land.Shape.BoundBox.ZMin / 1000)
        self.form.editTo.setSuffix(" m")
        self.form.editTo.setValue(land.Shape.BoundBox.ZMax / 1000)
        self.form.editSteps.setValue(10)
        self.form.editFrom.valueChanged.connect(self.updateTableValues)
        self.form.editTo.valueChanged.connect(self.updateTableValues)

    def accept(self):
        land = FreeCAD.ActiveDocument.Site.Terrain
        if land.isDerivedFrom("Part::Feature"):
            colorlist = []
            for face in land.Shape.Faces:
                zz = face.CenterOfMass.z / 1000
                color = (.0, .0, .0)
                for i in range(1,len(self.ranges)):
                    if self.ranges[i][0] <= zz <= self.ranges[i][1]:
                        color = self.ranges[i][2]
                        break
                colorlist.append(color)
            land.ViewObject.DiffuseColor = colorlist
        FreeCAD.activeDocument().recompute()
        return True

# Slope Analisys: ---------------------------------------------------------------------------------
class _SlopeTaskPanel(_generalTaskPanel):
    '''The TaskPanel for Slope setup'''

    def __init__(self):
        _generalTaskPanel.__init__(self)
        self.angles = self.getAngles()
        # Initial set-up:
        self.form.editFrom.setSuffix(" º")
        self.form.editFrom.setValue(0)
        self.form.editTo.setSuffix(" º")
        self.form.editTo.setValue(max(self.angles))
        self.form.editSteps.setValue(10)
        self.form.editFrom.valueChanged.connect(self.updateTableValues)
        self.form.editTo.valueChanged.connect(self.updateTableValues)

    def getAngles(self):
        import math
        land = FreeCAD.ActiveDocument.Site.Terrain
        angles = []
        for face in land.Shape.Faces:
            normal = face.normalAt(0, 0)
            rad = normal.getAngle(FreeCAD.Vector(0, 0, 1))
            angle = math.degrees(rad)
            angles.append(angle)
        return angles

    def getPointSlope(self, ranges = None):
        from datetime import datetime
        starttime = datetime.now()
        import math

        land = FreeCAD.ActiveDocument.Site.Terrain
        if land.isDerivedFrom("Part::Feature"):
            colorlist = []
            for face in land.Shape.Faces:
                normal = face.normalAt(0, 0)
                rad = normal.getAngle(FreeCAD.Vector(0, 0, 1))
                angle = math.degrees(rad)
                if(angle > 90):
                    angle -= 90
                color = (1.0, 1.0, 1.0)
                for i in range(0, len(ranges)):
                    if ranges[i][0] <= angle <= ranges[i][1]:
                        color = ranges[i][2]
                        break
                colorlist.append(color)
            print(len(land.Shape.Faces) == len(colorlist))
            land.ViewObject.DiffuseColor = colorlist

        # TODO: check this code:
        elif obj.isDerivedFrom("Mesh::Feature"):
            fMesh = Mest2FemMesh(land)
            import math
            setColors = []
            i = 1
            normals = land.Mesh.getPointNormals()
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

    def accept(self):
        # self.getPointSlope()
        import threading
        hilo = threading.Thread(target=self.getPointSlope(self.ranges))
        hilo.start()
        return True

# Orientation Analisys: ---------------------------------------------------------------------------------
class _OrientationTaskPanel(_generalTaskPanel):
    '''The TaskPanel for Orientation setup'''

    def __init__(self):
        _generalTaskPanel.__init__(self)

        self.getAngles()

        # Initial set-up:
        self.form.editFrom.setSuffix(" º")
        self.form.editFrom.setValue(0.0)
        self.form.editTo.setSuffix(" º")
        self.form.editTo.setMaximum(360.0)
        self.form.editTo.setValue(360.0)
        self.form.editSteps.setValue(15)
        self.form.editFrom.valueChanged.connect(self.updateTableValues)
        self.form.editTo.valueChanged.connect(self.updateTableValues)

    def getAngles(self):
        import math
        land = FreeCAD.ActiveDocument.Site.Terrain
        anglesx = []
        anglesy = []
        for face in land.Shape.Faces:
            normal = face.normalAt(0, 0)
            normal.z = 0
            anglesx.append(math.degrees(normal.getAngle(FreeCAD.Vector(1, 0, 0))))
            anglesy.append(math.degrees(normal.getAngle(FreeCAD.Vector(0, 1, 0))))

        print("Min x: ", min(anglesx), " y: ", min(anglesy))
        print("Max x: ", max(anglesx), " y: ", max(anglesy))
        return anglesx, anglesy

    def accept(self):
        import math
        from datetime import datetime
        starttime = datetime.now()

        land = FreeCAD.ActiveDocument.Site.Terrain
        print(land)
        if land.isDerivedFrom("Part::Feature"):
            colorlist = []
            j = 0
            minx = 99999
            miny = 99999
            for face in land.Shape.Faces:
                normal = face.normalAt(0, 0)
                normal.z = 0
                anglex = math.degrees(normal.getAngle(FreeCAD.Vector(1, 0, 0)))
                angley = math.degrees(normal.getAngle(FreeCAD.Vector(0, 1, 0)))

                minx = min([minx, anglex])
                miny = min([miny, angley])
                if angley >= 90:
                    anglex = 360.0 - anglex

                #print(anglex, " ", angley)
                for i in range(1, len(self.ranges)):
                    if self.ranges[i][0] <= anglex <= self.ranges[i][1]:
                        colorlist.append(self.ranges[i][2])
                        break
                j += 1
                if j == 100:
                    break
            land.ViewObject.DiffuseColor = colorlist
            print("Angulos: ", math.degrees(minx), " - ", miny)

        # TODO: check this code:
        elif land.isDerivedFrom("Mesh::Feature"):
            fMesh = Mest2FemMesh(land)
            import Mesh
            fMesh = Mest2FemMesh(land)

            setColors = {}
            i = 1
            normals = land.Mesh.getPointNormals()
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

## Commands ----------------------------------------------------------------------------------------------------------
## 1. Contours:
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

## 3. Height:
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

## 5. Commands
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