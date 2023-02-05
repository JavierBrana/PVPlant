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

import FreeCAD, FreeCADGui, Draft
from PySide import QtCore, QtGui, QtSvg
from PySide.QtCore import QT_TRANSLATE_NOOP

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import os, math
from PVPlantResources import DirIcons as DirIcons

class _TaskPanel:
    def __init__(self, obj = None):
        self.obj = None
        self.select = 0

        self.form = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/PVPlantCreateTerrainMesh.ui")
        self.form.buttonAdd.clicked.connect(self.add)

    def add(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.obj = sel[0]
            self.form.editCloud.setText(self.obj.Label)

    def MaxLength(self, P1, P2, P3, MaxlengthLE):
        """
        Calculation of the 2D length between triangle edges
        """

        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

        List = [[p1, p2], [p2, p3], [p3, p1]]
        for i, j in List:
            vec = i.sub(j)
            if vec.Length > MaxlengthLE:
                return False

        return True

    def MaxAngle(self, P1, P2, P3, MaxAngleLE):
        """
        Calculation of the 2D angle between triangle edges
        """

        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

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

        import Part
        import numpy as np
        from scipy.spatial import Delaunay

        bnd = FreeCAD.ActiveDocument.Site.Terrain.CuttingBoundary.Shape
        if len(bnd.Faces) == 0:
            bnd = Part.Face(bnd)

        # Get user input
        MaxlengthLE = int(self.form.MaxlengthLE.text()) * 1000
        MaxAngleLE = math.radians(int(self.form.MaxAngleLE.text()))

        firstPoint = self.obj.Points.Points[0]
        nbase = FreeCAD.Vector(firstPoint.x, firstPoint.y, firstPoint.z)
        data = []
        for point in self.obj.Points.Points:
            tmp = FreeCAD.Vector(0, 0, 0).add(point)
            tmp.z = 0
            if bnd.isInside(tmp, 0, True):
                p = point - nbase
                data.append([float(p.x), float(p.y), float(p.z)])

        Data = np.array(data)
        data.clear()

        ''' not working:
        import multiprocessing
        rows = Data.shape[0]

        cpus = multiprocessing.cpu_count()
        steps = math.ceil(rows / cpus)

        for cpu in range(cpus - 1):
            start = steps * cpu
            end = steps * (cpu + 1)
            if end > rows:
                end = rows - start
            tmp = Data[start : end, :]
            p = multiprocessing.Process(target = Triangulate, args = (tmp,))
            p.start()
            p.join()
        return
        '''

        # TODO: si es muy grande, dividir el cálculo de la maya en varias etapas
        # Create delaunay triangulation
        tri = Delaunay(Data[:, :2])
        print("tiempo delaunay:", datetime.now() - starttime)

        faces = tri.simplices
        from stl import mesh
        wireframe = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            if self.MaxLength(Data[f[0]], Data[f[1]], Data[f[2]], MaxlengthLE) and \
               self.MaxAngle(Data[f[0]], Data[f[1]], Data[f[2]], MaxAngleLE):
                for j in range(3):
                    wireframe.vectors[i][j] = Data[f[j], :]

        import Mesh
        MeshObject = Mesh.Mesh(wireframe.vectors.tolist())
        MeshObject.Placement.move(nbase)
        MeshObject.harmonizeNormals()
        Surface = FreeCAD.ActiveDocument.addObject("Mesh::Feature", self.form.SurfaceNameLE.text())
        Surface.Mesh = MeshObject
        Surface.Label = self.form.SurfaceNameLE.text()

        shape = MeshToShape(MeshObject)
        import Part
        Part.show(shape)

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()
        print(" --- Tiempo tardado:", datetime.now() - starttime)

    def reject(self):
        FreeCADGui.Control.closeDialog()



#----------------------------------------------------------------------------------------------
#from PySide.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication
from PySide.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool

import sys
import time
import traceback


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    - finished: No data
    - error: tuple (exctype, value, traceback.format_exc() )
    - result: object data returned from processing, anything
    - progress: int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    - param callback: The function callback to run on this worker thread. Supplied args and
                      kwargs will be passed through to the runner.
    - type callback: function
    - param args: Arguments to pass to the callback function
    - param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
#--------------------------------------------------------------------------------------------
def projectShapeOnMesh(shape, mesh):
    import MeshPart as mp
    tmp = mp.projectShapeOnMesh(shape, mesh, FreeCAD.Vector(0,0,1))
    pts = list()
    for points in tmp:
        pts.extend(points)
    res = [i for n, i in enumerate(pts) if i not in pts[:n]]
    return res

def Triangulate(Points, MaxlengthLE = 8000, MaxAngleLE = math.pi / 2):
    import numpy as np
    from scipy.spatial import Delaunay
    from stl import mesh as stlmesh
    import Mesh

    tri = Delaunay(Points[:, :2])
    faces = tri.simplices
    wireframe = stlmesh.Mesh(np.zeros(faces.shape[0], dtype=stlmesh.Mesh.dtype))

    for i, f in enumerate(faces):
        if MaxLength(Points[f[0]], Points[f[1]], Points[f[2]], MaxlengthLE) and \
           MaxAngle(Points[f[0]], Points[f[1]], Points[f[2]], MaxAngleLE):
            for j in range(3):
                wireframe.vectors[i][j] = Points[f[j], :]

    MeshObject = Mesh.Mesh(wireframe.vectors.tolist())
    if len(MeshObject.Facets) == 0:
        return None
    MeshObject.harmonizeNormals()
    if MeshObject.Facets[0].Normal.z < 0:
        MeshObject.flipNormals()
    return MeshObject

def MaxLength(P1, P2, P3, MaxlengthLE):
    """
    Calculation of the 2D length between triangle edges
    """
    p1 = FreeCAD.Vector(P1[0], P1[1], 0)
    p2 = FreeCAD.Vector(P2[0], P2[1], 0)
    p3 = FreeCAD.Vector(P3[0], P3[1], 0)

    List = [[p1, p2], [p2, p3], [p3, p1]]
    for i, j in List:
        vec = i.sub(j)
        if vec.Length > MaxlengthLE:
            return False
    return True

def MaxAngle(P1, P2, P3, MaxAngleLE):
    """
    Calculation of the 2D angle between triangle edges
    """
    p1 = FreeCAD.Vector(P1[0], P1[1], 0)
    p2 = FreeCAD.Vector(P2[0], P2[1], 0)
    p3 = FreeCAD.Vector(P3[0], P3[1], 0)
    List = [[p1, p2, p3], [p2, p3, p1], [p3, p1, p2]]
    for j, k, l in List:
        vec1 = j.sub(k)
        vec2 = l.sub(k)
        radian = vec1.getAngle(vec2)
        if radian > MaxAngleLE:
            return False
    return True

def Open3DTriangle(point_cloud):
    import numpy as np
    import open3d as o3d

    '''
    input_path = "your_path_to_file/"
    output_path = "your_path_to_output_folder/"
    dataname = "sample.xyz"
    point_cloud = np.loadtxt(input_path + dataname, skiprows=1)
    '''
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)

    pcd.normals = o3d.utility.Vector3dVector(np.zeros((1, 3)))
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(100)

    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd,
                                                                             depth=8,
                                                                             width=0,
                                                                             scale=1.1,
                                                                             linear_fit=False,
                                                                             n_threads=8)
    o3d.visualization.draw_geometries([mesh])
    #bbox = pcd.get_axis_aligned_bounding_box()
    #p_mesh_crop = mesh.crop(bbox)
    return mesh


def MeshToShape(mesh):
    import Part
    meshcopy = mesh.copy()
    meshcopy.Placement.Base = FreeCAD.Vector(0,0,0)
    shape = Part.Shape()
    shape.makeShapeFromMesh(meshcopy.Topology, 0.1)
    shape.Placement = mesh.Placement
    return shape


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
