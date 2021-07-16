import FreeCAD, FreeCADGui, Draft
from PySide import QtCore, QtGui, QtSvg
from PySide.QtCore import QT_TRANSLATE_NOOP

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import os
from PVPlantResources import DirIcons as DirIcons


class _TaskPanel:
    def __init__(self, obj = None):
        self.obj = None
        self.select = 0

        self.form = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/PVPlantCreateTerrainMesh.ui")
        self.form.buttonAdd.clicked.connect(self.add)

    ''' future:
    def retranslateUi(self, dialog):
        from PySide import QtGui
        self.form.setWindowTitle("Configuracion del Rack")
        self.labelModule.setText(QtGui.QApplication.translate("PVPlant", "Modulo:", None))
        self.labelModuleLength.setText(QtGui.QApplication.translate("PVPlant", "Longitud:", None))
        self.labelModuleWidth.setText(QtGui.QApplication.translate("PVPlant", "Ancho:", None))
        self.labelModuleHeight.setText(QtGui.QApplication.translate("PVPlant", "Alto:", None))
        self.labelModuleFrame.setText(QtGui.QApplication.translate("PVPlant", "Ancho del marco:", None))
        self.labelModuleColor.setText(QtGui.QApplication.translate("PVPlant", "Color del modulo:", None))
        self.labelModules.setText(QtGui.QApplication.translate("Arch", "Colocacion de los Modulos", None))
        self.labelModuleOrientation.setText(QtGui.QApplication.translate("Arch", "Orientacion del modulo:", None))
        self.labelModuleGapX.setText(QtGui.QApplication.translate("Arch", "Separacion Horizontal (mm):", None))
        self.labelModuleGapY.setText(QtGui.QApplication.translate("Arch", "Separacion Vertical (mm):", None))
        self.labelModuleRows.setText(QtGui.QApplication.translate("Arch", "Filas de modulos:", None))
        self.labelModuleCols.setText(QtGui.QApplication.translate("Arch", "Columnas de modulos:", None))
        self.labelRack.setText(QtGui.QApplication.translate("Arch", "Configuracion de la estructura", None))
        self.labelRackType.setText(QtGui.QApplication.translate("Arch", "Tipo de estructura:", None))
        self.labelLevel.setText(QtGui.QApplication.translate("Arch", "Nivel:", None))
        self.labelOffset.setText(QtGui.QApplication.translate("Arch", "Offset", None))
    '''

    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.form.editCloud.setText(self.obj.Label)

    def MaxLength(self, P1, P2, P3):
        """
        Calculation of the 2D length between triangle edges
        """
        # Get user input
        MaxlengthLE = int(self.form.MaxlengthLE.text()) * 1000

        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

        # Calculate length between triangle vertices
        List = [[p1, p2], [p2, p3], [p3, p1]]
        for i, j in List:
            vec1 = i.sub(j)
            if vec1.Length > MaxlengthLE:
                return False
        return True

    def MaxAngle(self, P1, P2, P3):
        """
        Calculation of the 2D angle between triangle edges
        """
        import math

        # Get user input
        MaxAngleLE = math.radians(int(self.form.MaxAngleLE.text()))

        import math
        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

        # Calculate angle between triangle vertices
        List = [[p1, p2, p3], [p2, p3, p1], [p3, p1, p2]]
        for j, k, l in List:
            vec1 = j.sub(k)
            vec2 = l.sub(k)
            radian = vec1.getAngle(vec2)

            if radian > MaxAngleLE:
                return False

        return True

    def accept(self):
        from datetime import datetime
        starttime = datetime.now()

        import numpy as np
        from scipy.spatial import Delaunay

        test = []
        for Point in self.obj.Points.Points:
            test.append([float(Point.x), float(Point.y), float(Point.z)])

        nbase = FreeCAD.Vector(test[0][0], test[0][1], test[0][2])
        data = []
        for i in test:
            data.append([i[0] - nbase.x, i[1] - nbase.y, i[2] - nbase.z])
        Data = np.array(data)
        test.clear()
        data.clear()

        # TODO: si es muy grande, dividir el cálculo de la maya en varias etapas
        # Create delaunay triangulation
        tri = Delaunay(Data[:, :2])
        print("tiempo delaunay:", datetime.now() - starttime)
        starttime = datetime.now()

        List = []
        for i in tri.vertices:
            first = int(i[0])
            second = int(i[1])
            third = int(i[2])

            # Test triangle
            if self.MaxLength(Data[first], Data[second], Data[third]) \
                    and self.MaxAngle(Data[first], Data[second], Data[third]):
                List.append(Data[first])
                List.append(Data[second])
                List.append(Data[third])
        print("tiempo filtro:", datetime.now() - starttime)
        starttime = datetime.now()
        print(List)
        return

        useMesh = False
        if useMesh:
            MeshList = []
            for i in tri.vertices:
                first = int(i[0])
                second = int(i[1])
                third = int(i[2])

                #Test triangle
                if self.MaxLength(Data[first], Data[second], Data[third])\
                        and self.MaxAngle(Data[first], Data[second], Data[third]):
                    MeshList.append(Data[first])
                    MeshList.append(Data[second])
                    MeshList.append(Data[third])

            import Mesh
            MeshObject = Mesh.Mesh(MeshList)
            MeshObject.Placement.move(nbase)
            Surface = FreeCAD.ActiveDocument.addObject("Mesh::Feature", self.form.SurfaceNameLE.text())
            Surface.Mesh = MeshObject
            Surface.Label = self.form.SurfaceNameLE.text()

        else:
            import Part
            from array import array
            faces = []
            cnt = 0
            print("triangles: ")
            print(tri.vertices, "\n")
            for i in tri.vertices:
                first = int(i[0])
                second = int(i[1])
                third = int(i[2])

                #print(i, " ", i.tolist())
                print(array(Data[first].tolist()))

                #Test triangle
                #if self.MaxLength(Data[first], Data[second], Data[third])\
                #        and self.MaxAngle(Data[first], Data[second], Data[third]):

                vertexes = [(Data[first][0],  Data[first][1],  Data[first][2]),
                            (Data[second][0], Data[second][1], Data[second][2]),
                            (Data[third][0],  Data[third][1],  Data[third][2]),
                            (Data[first][0],  Data[first][1],  Data[first][2])]

                print("       ----", vertexes)
                polygon = Part.makePolygon(vertexes)
                Part.show(polygon)
                faces.append(Part.Face(polygon))

                cnt += 1
                if cnt == 5:
                    break

                """
                array = [[FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 1), FreeCAD.Vector(2, 0, 0)],
                         [FreeCAD.Vector(0, 1, 1), FreeCAD.Vector(1, 1, 2), FreeCAD.Vector(2, 1, 1)],
                         [FreeCAD.Vector(0, 2, 0), FreeCAD.Vector(1, 2, 1.5), FreeCAD.Vector(2, 2, 0)],
                         [FreeCAD.Vector(0, 3, 0), FreeCAD.Vector(1, 3, 0), FreeCAD.Vector(2, 3, 0.5)]]

                # Display the points

                v = []
                for row in array:
                    for point in row:
                        v.append(Part.Vertex(point))

                c = Part.Compound(v)
                Part.show(c)

                # Generate an interpolating surface

                intSurf = Part.BSplineSurface()
                intSurf.interpolate(array)

                # Generate an approximating surface

                appSurf = Part.BSplineSurface()
                appSurf.approximate(Points=array)

                # Display the surfaces

                Part.show(intSurf.toShape())
                Part.show(appSurf.toShape())
                """

            Part.show(Part.makeCompound(faces))
            shell = Part.makeShell(faces)
            Part.show(shell, "Land")

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()
        print("tiempo: tardado", datetime.now() - starttime)

    def reject(self):
        FreeCADGui.Control.closeDialog()



class _PVPlantCreateTerrainMesh:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "surface.svg")),
                'MenuText': QT_TRANSLATE_NOOP("PVPlant", "Create Surface"),
                'Accel': "C, S",
                'ToolTip': QT_TRANSLATE_NOOP("PVPlant", "Creates a surface form a cloud of points.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _TaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantCreateTerrainMesh', _PVPlantCreateTerrainMesh())