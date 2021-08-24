import math
import FreeCAD, Draft
import ArchComponent
import PVPlantSite, Part

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

    import Part
    import pivy
    from pivy import coin
    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "FreeCAD Fixed Rack"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")

DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")


def makeTerrain(name="Terrain"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Terrain")
    obj.Label = name
    _Terrain(obj)
    _ViewProviderTerrain(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class _Terrain(ArchComponent.Component):
    "A Shadow Terrain Obcject"

    def __init__(self, obj):
        # Definición de  variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        self.obj = obj
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False

        site = PVPlantSite.get()
        site.Terrain = obj

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
                        "CuttingBoundary",
                        "Surface",
                        "A boundary line to delimit the surface")

        obj.addProperty("App::PropertyFile",
                        "DEM",
                        "Surface",
                        "Load a ASC file to generate the surface")

        obj.addProperty("App::PropertyFile",
                        "PointsGroup",
                        "Surface",
                        "Use a Point Group to generate the surface")



        obj.addProperty("App::PropertyLinkList",
                        "AllowedAreas",
                        "Areas",
                        "A boundary to delimitated the terrain").AllowedAreas=[]

        obj.addProperty("App::PropertyLinkList",
                        "ProhibitedAreas",
                        "Areas",
                        "A boundary to delimitated the terrain").ProhibitedAreas=[]



    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = stat

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''
        if prop == "DEM" or prop == "CuttingBoundary":
            if obj.DEM and obj.CuttingBoundary:
                import numpy as np

                grid_space = 1

                file = open(obj.DEM, "r")
                templist = [line.split() for line in file.readlines()]
                file.close()
                del file

                # Read meta data:
                meta = templist[0:6]
                nx = int(meta[0][1])  # NCOLS
                ny = int(meta[1][1])  # NROWS
                xllcorner = round(float(meta[2][1]), 3)  # XLLCENTER
                yllcorner = round(float(meta[3][1]), 3)  # YLLCENTER
                cellsize = round(float(meta[4][1]), 3)  # CELLSIZE
                nodata_value = float(meta[5][1])  # NODATA_VALUE

                # set coarse_factor
                coarse_factor = max(round(grid_space / cellsize), 1)

                # Get z values
                templist = templist[6:(6 + ny)]
                templist = [templist[i][0::coarse_factor] for i in np.arange(0, len(templist), coarse_factor)]
                datavals = np.array(templist).astype(float)
                templist.clear()

                # create xy coordinates
                x = cellsize * np.arange(nx)[0::coarse_factor] + xllcorner
                y = cellsize * np.arange(ny)[-1::-1][0::coarse_factor] + yllcorner

                site = PVPlantSite.get()
                if obj.CuttingBoundary:
                    inc_x = obj.CuttingBoundary.Shape.BoundBox.XLength * 0.05
                    inc_y = obj.CuttingBoundary.Shape.BoundBox.YLength * 0.05

                    min_x = 0
                    max_x = 0

                    comp = (obj.CuttingBoundary.Shape.BoundBox.XMin - inc_x) / 1000
                    for i in range(nx):
                        if x[i] > comp:
                            min_x = i - 1
                            break
                    comp = (obj.CuttingBoundary.Shape.BoundBox.XMax + inc_x) / 1000
                    for i in range(min_x, nx):
                        if x[i] > comp:
                            max_x = i
                            break

                    min_y = 0
                    max_y = 0

                    comp = (obj.CuttingBoundary.Shape.BoundBox.YMax + inc_y) / 1000
                    for i in range(ny):
                        if y[i] < comp:
                            max_y = i
                            break
                    comp = (obj.CuttingBoundary.Shape.BoundBox.YMin - inc_y) / 1000
                    for i in range(max_y, ny):
                        if y[i] < comp:
                            min_y = i
                            break

                    x = x[min_x:max_x]
                    y = y[max_y:min_y]
                    datavals = datavals[max_y:min_y, min_x:max_x]

                pts = []

                if False:  # faster but more memory 46s - 4,25 gb
                    x, y = np.meshgrid(x, y)
                    xx = x.flatten()
                    yy = y.flatten()
                    zz = datavals.flatten()
                    x[:] = 0
                    y[:] = 0
                    datavals[:] = 0

                    for i in range(0, len(xx)):
                        pts.append(FreeCAD.Vector(xx[i], yy[i], zz[i]) * 1000)

                    xx[:] = 0
                    yy[:] = 0
                    zz[:] = 0

                else:  # 51s 3,2 gb
                    createmesh = True
                    if createmesh:
                        lines = []
                        for j in range(len(y)):
                            edges = []
                            for i in range(0, len(x) - 1):
                                ed = Part.makeLine(FreeCAD.Vector(x[i], y[j], datavals[j][i]) * 1000,
                                                   FreeCAD.Vector(x[i + 1], y[j], datavals[j][i + 1]) * 1000)
                                edges.append(ed)
                            line = Part.Wire(edges)
                            lines.append(line)
                        p = Part.makeLoft(lines, False, True, False)
                        p = Part.Solid(p)
                        obj.Shape = p
                    else:
                        pts = []
                        for j in range(ny):
                            for i in range(nx):
                                pts.append(FreeCAD.Vector(x[i], y[j], datavals[j][i]) * 1000)

                pts.clear()



    def execute(self, obj):
        print("  -----  Terrain  -  EXECUTE  ----------")



class _ViewProviderTerrain(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "terrain.svg"))

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # GeoCoords Node.
        self.geo_coords = coin.SoGeoCoordinate()


class _TerrainTaskPanel:

    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")

    def accept(self):
        makeTerrain()
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


class _CommandTerrain:
    "the PVPlant Terrain command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "terrain.svg")),
                'MenuText': "Terrain",
                'Accel': "S, T",
                'ToolTip':"Creates a Terrain object from setup dialog."}

    #def IsActive(self):
    #    return not FreeCAD.ActiveDocument is None

    def IsActive(self):
        return True
        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for o in FreeCAD.ActiveDocument.Objects:
                    if o.Name[:4] == "Site":
                        return True

        return False

    def Activated(self):
        task = _TerrainTaskPanel()
        FreeCADGui.Control.showDialog(task)
        return


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Terrain', _CommandTerrain())