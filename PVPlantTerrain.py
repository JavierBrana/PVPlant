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
import Part
import PVPlantSite
import copy

if FreeCAD.GuiUp:
    import FreeCADGui
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
        obj.ViewObject.ShapeColor = (.0000, 0.6667, 0.4980)
        obj.ViewObject.LineColor = (0.0000, 0.6000, 0.4392)

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


        pl = obj.PropertiesList
        if not "CuttingBoundary" in pl:
            obj.addProperty("App::PropertyLink",
                            "CuttingBoundary",
                            "Surface",
                            "A boundary line to delimit the surface")
        if not "DEM" in pl:
            obj.addProperty("App::PropertyFile",
                            "DEM",
                            "Surface",
                            "Load a ASC file to generate the surface")
        if not "PointsGroup" in pl:
            obj.addProperty("App::PropertyLink",
                            "PointsGroup",
                            "Surface",
                            "Use a Point Group to generate the surface")

        '''
        if not "AllowedAreas" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "AllowedAreas",
                            "Areas",
                            "A boundary to delimitated the terrain").AllowedAreas = []
        if not "ProhibitedAreas" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "ProhibitedAreas",
                            "Areas",
                            "A boundary to delimitated the terrain").ProhibitedAreas = []
        '''

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

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

                # remove points out of area
                # 1. coarse:
                inc_x = obj.CuttingBoundary.Shape.BoundBox.XLength * 0.0
                inc_y = obj.CuttingBoundary.Shape.BoundBox.YLength * 0.0

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

                # 2. fine: TODO: ----

                if False:  # faster but more memory 46s - 4,25 gb
                    x, y = np.meshgrid(x, y)
                    xx = x.flatten()
                    yy = y.flatten()
                    zz = datavals.flatten()
                    x[:] = 0
                    y[:] = 0
                    datavals[:] = 0
                    pts = []
                    for i in range(0, len(xx)):
                        pts.append(FreeCAD.Vector(xx[i], yy[i], zz[i]) * 1000)

                    xx[:] = 0
                    yy[:] = 0
                    zz[:] = 0

                    import PVPlantCreateTerrainMesh
                    PVPlantCreateTerrainMesh.Triangulate()

                else:  # 51s 3,2 gb
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
                pts.clear()

        if prop == "PointsGroup" or prop == "CuttingBoundary":
            if obj.PointsGroup and obj.CuttingBoundary:
                import numpy as np
                bnd = obj.CuttingBoundary.Shape
                if len(bnd.Faces) == 0:
                    bnd = Part.Face(bnd)

                # TODO: not use the first point, else the Origin in "Site".
                #  It is standar for everything.
                firstPoint = self.obj.PointsGroup.Points.Points[0]
                nbase = FreeCAD.Vector(firstPoint.x, firstPoint.y, firstPoint.z)
                data = []
                for point in self.obj.PointsGroup.Points.Points:
                    tmp = FreeCAD.Vector(0, 0, 0).add(point)
                    tmp.z = 0
                    if bnd.isInside(tmp, 0, True):
                        p = point - nbase
                        data.append([float(p.x), float(p.y), float(p.z)])

                Data = np.array(data)
                data.clear()

                import PVPlantCreateTerrainMesh
                mesh = PVPlantCreateTerrainMesh.Triangulate(Data)
                shape = PVPlantCreateTerrainMesh.MeshToShape(mesh)
                shape.Placement.move(nbase)

                obj.Shape = shape
                if obj.DEM:
                    obj.DEM = None

    def execute(self, obj):
        print("  -----  Terrain  -  EXECUTE  ----------")


class _ViewProviderTerrain(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)
        vobj.Proxy = self

    def getIcon(self):
        return str(os.path.join(DirIcons, "terrain.svg"))

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object

        # GeoCoords Node.
        self.geo_coords = coin.SoGeoCoordinate()

        # Surface features.
        self.triangles = coin.SoIndexedFaceSet()
        # print(self.triangles)
        self.face_material = coin.SoMaterial()
        self.edge_material = coin.SoMaterial()
        self.edge_color = coin.SoBaseColor()
        self.edge_style = coin.SoDrawStyle()
        self.edge_style.style = coin.SoDrawStyle.LINES

        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.PER_FACE
        offset = coin.SoPolygonOffset()

        # Face root.
        faces = coin.SoSeparator()
        faces.addChild(shape_hints)
        faces.addChild(self.face_material)
        faces.addChild(mat_binding)
        faces.addChild(self.geo_coords)
        faces.addChild(self.triangles)

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        faces.addChild(shape_hints)
        highlight.addChild(self.edge_material)
        highlight.addChild(mat_binding)
        highlight.addChild(self.edge_style)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        origin = PVPlantSite.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        # Set geosystem.
        geo_system = ["UTM", origin.UtmZone, "FLAT"]
        self.geo_coords.geoSystem.setValues(geo_system)
        '''
        self.boundary_coords.geoSystem.setValues(geo_system)
        self.major_coords.geoSystem.setValues(geo_system)
        self.minor_coords.geoSystem.setValues(geo_system)
        '''

        if prop == "Shape":
            shape = obj.getPropertyByName(prop)
            # Get GeoOrigin.
            points = [ver.Point for ver in shape.Vertexes]
            self.geo_coords.point.values = points

    def claimChildren(self):
        """Define which objects will appear as children in the tree view.

        Set objects within the site group, and the terrain object as children.

        If the Arch preference swallowSubtractions is true, set the additions
        and subtractions to the terrain as children.

        Returns
        -------
        list of <App::DocumentObject>s:
            The objects claimed as children.
        """

        return [self.Object.CuttingBoundary, ]


class _TerrainTaskPanel:

    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantTerrain.ui")

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
                'ToolTip': "Creates a Terrain object from setup dialog."}

    # def IsActive(self):
    #    return not FreeCAD.ActiveDocument is None

    def IsActive(self):
        if FreeCAD.ActiveDocument.getObject("Site") is None:
            return False
        return True

    def Activated(self):
        makeTerrain()
        # task = _TerrainTaskPanel()
        # FreeCADGui.Control.showDialog(task)
        return


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Terrain', _CommandTerrain())
