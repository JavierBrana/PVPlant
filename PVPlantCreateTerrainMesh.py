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
        MaxlengthLE = self.form.MaxlengthLE.text()

        new = False
        if new:
            tri = [[P1, P2], [P2, P3], [P3, P1]]
            for i, j in tri:
                vec = i.sub(j)

                # Compare with input
                if vec.Length > MaxlengthLE:
                    return False
            return True
        else:
            p1 = FreeCAD.Vector(P1[0], P1[1], 0)
            p2 = FreeCAD.Vector(P2[0], P2[1], 0)
            p3 = FreeCAD.Vector(P3[0], P3[1], 0)

            # Calculate length between triangle vertices
            List = [[p1, p2], [p2, p3], [p3, p1]]
            for i, j in List:
                vec1 = i.sub(j)

                # Compare with input
                if vec1.Length > int(MaxlengthLE) * 1000:
                    return False
            return True

    def MaxAngle(self, P1, P2, P3):
        """
        Calculation of the 2D angle between triangle edges
        """
        # Get user input
        MaxAngleLE = self.form.MaxAngleLE.text()

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
            degree = math.degrees(radian)

            # Compare with input
            if degree > int(MaxAngleLE):
                return False

        return True

    def accept(self):
        import numpy as np
        import scipy.spatial

        # Print warning if there isn't selected group
        #if len(self.form.PointGroupsLV.selectedIndexes()) < 1:
        #    FreeCAD.Console.PrintMessage("No Points object selected")
        #    return

        # Get selected group(s) points
        test = []
        for Point in self.obj.Points.Points:
            test.append([float(Point.x), float(Point.y), float(Point.z)])

        # Normalize points
        fpoint = test[0]
        nbase = FreeCAD.Vector(fpoint[0], fpoint[1], fpoint[2])
        #scale_factor = FreeCAD.Vector(base.x / 1677.7216, base.y / 1677.7216, base.Z / 1677.7216)
        #nbase = scale_factor.multiply(1677.7216)

        data = []
        for i in test:
            data.append([i[0] - nbase.x, i[1] - nbase.y, i[2] - nbase.z])
        Data = np.array(data)
        del test
        del data

        # Create delaunay triangulation
        tri = scipy.spatial.Delaunay(Data[:, :2])

        print (tri)

        useMesh = True
        new = False
        if useMesh:
            if new:
                import copy

                delaunay = []
                for i in tri.vertices.tolist():
                    delaunay.extend(i)
                del tri

                base = copy.deepcopy(origin)
                base.z = 0
                index = []
                mesh_index = []

                for i in range(0, len(delaunay), 3):
                    first, second, third = delaunay[i:i + 3]

                    p1 = copy.deepcopy(points[first])
                    p2 = copy.deepcopy(points[second])
                    p3 = copy.deepcopy(points[third])
                    p1.z = p2.z = p3.z = 0

                    # Test triangle
                    if self.max_length(lmax, p1, p2, p3) \
                            and self.max_angle(amax, p1, p2, p3):
                        index.extend([first, second, third])

                for i in index:
                    mesh_index.append(points[i].sub(base))

            else:
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
            faces = []
            for i in tri.vertices:
                first = int(i[0])
                second = int(i[1])
                third = int(i[2])

                #Test triangle
                if self.MaxLength(Data[first], Data[second], Data[third])\
                        and self.MaxAngle(Data[first], Data[second], Data[third]):

                    polygon = Part.makePolygon([(Data[first][0], Data[first][1], Data[first][2]),
                                                (Data[second][0], Data[second][1], Data[second][2]),
                                                (Data[third][0], Data[third][1], Data[third][2]),
                                                (Data[first][0], Data[first][1], Data[first][2])])
                    faces.append(Part.makeFilledFace(polygon.Edges))

            #shell = Part.makeShell(faces)
            #solid = Part.Solid(shell).removeSplitter()
            #if solid.Volume < 0:
            #    solid.reverse()
            #Part.show(solid)


        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()

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