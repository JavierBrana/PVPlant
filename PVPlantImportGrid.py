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

import urllib.request, json
from PySide import QtCore, QtGui, QtSvg
from PySide.QtCore import QT_TRANSLATE_NOOP


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

import os
from PVPlantResources import DirIcons as DirIcons
import PVPlantSite


def get_elevation(lat=None, long=None):
    '''
        script for returning elevation in m from lat, long
    '''
    from requests import get
    from pandas import json_normalize

    if lat is None or long is None: return None

    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')

    # Request with a timeout for slow responses
    r = get(query, timeout=20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = json_normalize(r.json(), 'results')['elevation'].values[0]
    else:
        elevation = None
    return elevation

def getSinglePointElevationFromBing(lat, lng):
    #http://dev.virtualearth.net/REST/v1/Elevation/List?points={lat1,long1,lat2,long2,latN,longnN}&heights={heights}&key={BingMapsAPIKey}
    source = "http://dev.virtualearth.net/REST/v1/Elevation/List?points="
    source += str(lat) + "," + str(lng)
    source += "&heights=sealevel"
    source += "&key=AmsPZA-zRt2iuIdQgvXZIxme2gWcgLaz7igOUy7VPB8OKjjEd373eCnj1KFv2CqX"

    import requests
    response = requests.get(source)
    ans = response.text

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['resourceSets'][0]['resources'][0]['elevations']
    
    import utm
    for elevation in res:
        c = utm.from_latlon(lat, lng)
        v = FreeCAD.Vector(
            round(c[0] * 1000, 4),
            round(c[1] * 1000, 4),
            round(elevation * 1000, 4))
        return v

def getGridElevationFromBing(polygon, lat, lng, resolution = 1000):
    #http://dev.virtualearth.net/REST/v1/Elevation/Polyline?points=35.89431,-110.72522,35.89393,-110.72578,35.89374,-110.72606,35.89337,-110.72662
    # &heights=ellipsoid&samples=10&key={BingMapsAPIKey}
    import utm
    import math
    import requests
    import requests


    geo = utm.from_latlon(lat, lng)
    # result = (679434.3578335291, 4294023.585627955, 30, 'S')
    # EASTING, NORTHING, ZONE NUMBER, ZONE LETTER

    #StepsXX = int((polygon.Shape.BoundBox.XMax - polygon.Shape.BoundBox.XMin) / (resolution*1000))
    points = []
    yy = polygon.Shape.BoundBox.YMax
    while yy > polygon.Shape.BoundBox.YMin:
        xx = polygon.Shape.BoundBox.XMin
        while xx < polygon.Shape.BoundBox.XMax:
            StepsXX = int(math.ceil((polygon.Shape.BoundBox.XMax - xx) / resolution))

            if StepsXX > 1000:
                StepsXX = 1000
                xx1 = xx + 1000 * resolution
            else:
                xx1 = xx + StepsXX * resolution

            point1 = utm.to_latlon(xx / 1000, yy / 1000, geo[2], geo[3])
            point2 = utm.to_latlon(xx1 / 1000, yy / 1000, geo[2], geo[3])

            source = "http://dev.virtualearth.net/REST/v1/Elevation/Polyline?points="
            source += "{lat1},{lng1}".format(lat1=point1[0], lng1=point1[1])
            source += ","
            source += "{lat2},{lng2}".format(lat2=point2[0], lng2=point2[1])
            source += "&heights=sealevel"
            source += "&samples={steps}".format(steps=StepsXX)
            source += "&key=AmsPZA-zRt2iuIdQgvXZIxme2gWcgLaz7igOUy7VPB8OKjjEd373eCnj1KFv2CqX"

            response = requests.get(source)
            ans = response.text

            # +# to do: error handling  - wait and try again
            s = json.loads(ans)
            res = s['resourceSets'][0]['resources'][0]['elevations']

            i = 0
            for elevation in res:
                v = FreeCAD.Vector(xx + resolution * i, yy, round(elevation * 1000, 4))
                points.append(v)
                i += 1
            xx = xx1 + resolution # para no repetir un mismo punto
        yy -= resolution

    return points

def getSinglePointElevation(lat, lon):
    source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
    source += str(lat) + "," + str(lon)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"
    #print (source)

    #response = request.urlopen(source)
    #ans = response.read()
    import requests
    response = requests.get(source)
    ans = response.text

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']

    from geopy.distance import geodesic
    for r in res:

        reference = (0.0, 0.0)
        v = FreeCAD.Vector(
            round(geodesic(reference, (0.0, r['location']['lng'])).m, 2),
            round(geodesic(reference, (r['location']['lat'], 0.0)).m, 2),
            round(r['elevation'] * 1000, 2)
        )

    return v

def _getSinglePointElevation(lat, lon):
    source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
    source += str(lat) + "," + str(lon)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"
    #print (source)

    #response = request.urlopen(source)
    #ans = response.read()
    import requests
    response = requests.get(source)
    ans = response.text

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']

    import pymap3d as pm
    for r in res:
        x, y, z = pm.geodetic2ecef(round(r['location']['lng'], 2),
                                   round(r['location']['lat'], 2),
                                   0)
        v = FreeCAD.Vector(x,y,z)

    return v

def getSinglePointElevation1(lat, lon):
    source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
    source += str(lat) + "," + str(lon)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"

    #response = urllib.request.urlopen(source)
    #ans = response.read()
    import requests
    response = requests.get(source)
    ans = response.text

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']

    for r in res:
        c = tm.fromGeographic(r['location']['lat'], r['location']['lng'])
        v = FreeCAD.Vector(
            round(c[0], 4),
            round(c[1], 4),
            round(r['elevation'] * 1000, 2)
            )
    return v

def getSinglePointElevationUtm(lat, lon):
    source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
    source += str(lat) + "," + str(lon)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"
    print(source)

    #response = urllib.request.urlopen(source)
    #ans = response.read()
    import requests
    response = requests.get(source)
    ans = response.text

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']
    print (res)

    import utm
    for r in res:
        c = utm.from_latlon(r['location']['lat'], r['location']['lng'])
        v = FreeCAD.Vector(
            round(c[0] * 1000, 4),
            round(c[1] * 1000, 4),
            round(r['elevation'] * 1000, 2))
        print (v)
        return v


def getElevationUTM(polygon, lat, lng, resolution = 10000):

    import utm
    geo = utm.from_latlon(lat, lng)
    # result = (679434.3578335291, 4294023.585627955, 30, 'S')
    # EASTING, NORTHING, ZONE NUMBER, ZONE LETTER

    StepsXX = int((polygon.Shape.BoundBox.XMax - polygon.Shape.BoundBox.XMin) / (resolution*1000))
    points = []
    yy = polygon.Shape.BoundBox.YMax
    while yy > polygon.Shape.BoundBox.YMin:
        # utm.to_latlon(EASTING, NORTHING, ZONE NUMBER, ZONE LETTER).
        # result = (LATITUDE, LONGITUDE)
        point1 = utm.to_latlon(polygon.Shape.BoundBox.XMin / 1000, yy / 1000, geo[2], geo[3])
        point2 = utm.to_latlon(polygon.Shape.BoundBox.XMax / 1000, yy / 1000, geo[2], geo[3])

        source = "https://maps.googleapis.com/maps/api/elevation/json?path="
        source += "{a},{b}".format(a = point1[0], b = point1[1])
        source += "|"
        source += "{a},{b}".format(a = point2[0], b = point2[1])
        source += "&samples={a}".format(a = StepsXX)
        source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"

        import requests
        response = requests.get(source)
        ans = response.text

        # +# to do: error handling  - wait and try again
        s = json.loads(ans)
        res = s['results']


        for r in res:
            c = utm.from_latlon(r['location']['lat'], r['location']['lng'])
            v = FreeCAD.Vector(
                round(c[0] * 1000, 2),
                round(c[1] * 1000, 2),
                round(r['elevation'] * 1000, 2)
            )
            points.append(v)
        yy -= (resolution*1000)

    FreeCAD.activeDocument().recompute()
    return points

def getElevation1(polygon,resolution=10):

    StepsXX = int((polygon.Shape.BoundBox.XMax - polygon.Shape.BoundBox.XMin) / (resolution * 1000))
    points = []
    yy = polygon.Shape.BoundBox.YMax
    while yy > polygon.Shape.BoundBox.YMin:
        point1 = tm.toGeographic(polygon.Shape.BoundBox.XMin, yy)
        point2 = tm.toGeographic(polygon.Shape.BoundBox.XMax, yy)

        source = "https://maps.googleapis.com/maps/api/elevation/json?path="
        source += "{a},{b}".format(a = point1[0], b = point1[1])
        source += "|"
        source += "{a},{b}".format(a = point2[0], b = point2[1])
        source += "&samples={a}".format(a = StepsXX)
        source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"

        try:
            #response = urllib.request.urlopen(source)
            #ans = response.read()
            import requests
            response = requests.get(source)
            ans = response.text

            # +# to do: error handling  - wait and try again

            s = json.loads(ans)
            res = s['results']
        except:
            continue

        #points = []
        for r in res:
            c = tm.fromGeographic(r['location']['lat'], r['location']['lng'])
            v = FreeCAD.Vector(
                round(c[0], 2),
                round(c[1], 2),
                round(r['elevation'] * 1000, 2)
            )
            points.append(v)

        FreeCAD.activeDocument().recompute()
        yy -= (resolution*1000)

    return points

## download the heights from google:
def getElevation(lat, lon, b=50.35, le=11.17, size=40):
    #https://maps.googleapis.com/maps/api/elevation/json?path=36.578581,-118.291994|36.23998,-116.83171&samples=3&key=YOUR_API_KEY
    #https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key=YOUR_API_KEY

    source = "https://maps.googleapis.com/maps/api/elevation/json?path="
    source += str(b-size*0.001) + "," + str(le) + "|" + str(b+size*0.001) + "," + str(le)
    source += "&samples=" + str(100)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"

    response = urllib.request.urlopen(source)
    ans = response.read()

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']

    from geopy.distance import geodesic
    points = []
    for r in res:
        reference = (0.0, 0.0)
        v = FreeCAD.Vector(
            round(geodesic(reference, (0.0, r['location']['lat'])).m, 2),
            round(geodesic(reference, (r['location']['lng'], 0.0)).m, 2),
            round(r['elevation'] * 1000, 2) - baseheight
        )
        points.append(v)

    line = Draft.makeWire(points, closed=False, face=False, support=None)
    line.ViewObject.Visibility = False
    #FreeCAD.activeDocument().recompute()
    FreeCADGui.updateGui()
    return FreeCAD.activeDocument().ActiveObject


'''
# original::
def getElevation(lat, lon, b=50.35, le=11.17, size=40):
    tm.lat = lat
    tm.lon = lon
    baseheight = 0 #getheight(tm.lat, tm.lon)
    center = tm.fromGeographic(tm.lat, tm.lon)

    #https://maps.googleapis.com/maps/api/elevation/json?path=36.578581,-118.291994|36.23998,-116.83171&samples=3&key=YOUR_API_KEY
    #https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key=YOUR_API_KEY

    source = "https://maps.googleapis.com/maps/api/elevation/json?path="
    source += str(b-size*0.001) + "," + str(le) + "|" + str(b+size*0.001) + "," + str(le)
    source += "&samples=" + str(100)
    source += "&key=AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"

    response = urllib.request.urlopen(source)
    ans = response.read()

    # +# to do: error handling  - wait and try again
    s = json.loads(ans)
    res = s['results']

    points = []
    for r in res:
        c = tm.fromGeographic(r['location']['lat'], r['location']['lng'])
        v = FreeCAD.Vector(
            round(c[0], 2),
            round(c[1], 2),
            round(r['elevation'] * 1000, 2) - baseheight
        )
        points.append(v)

    line = Draft.makeWire(points, closed=False, face=False, support=None)
    line.ViewObject.Visibility = False
    #FreeCAD.activeDocument().recompute()
    FreeCADGui.updateGui()
    return FreeCAD.activeDocument().ActiveObject
'''

class _ImportPointsTaskPanel:

    def __init__(self, obj = None):
        self.obj = None
        self.Boundary = None
        self.select = 0
        self.filename = ""

        # form:
        self.form1 = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/PVPlantImportGrid.ui")
        self.form1.radio1.toggled.connect(lambda: self.mainToggle(self.form1.radio1))
        self.form1.radio2.toggled.connect(lambda: self.mainToggle(self.form1.radio2))
        self.form1.radio1.setChecked(True)  # << --------------Poner al final para que no dispare antes de crear los componentes a los que va a llamar
        #self.form.buttonAdd.clicked.connect(self.add)
        self.form1.buttonDEM.clicked.connect(self.openFileDEM)

        self.form2 = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/PVPlantCreateTerrainMesh.ui")
        #self.form2.buttonAdd.clicked.connect(self.add)
        self.form2.buttonBoundary.clicked.connect(self.addBoundary)


        #self.form = [self.form1, self.form2]
        self.form = self.form1

    ''' future:
    def retranslateUi(self, dialog):
        self.form1.setWindowTitle("Configuracion del Rack")
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
            self.lineEdit1.setText(self.obj.Label)

    def addBoundary(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.Boundary = sel[0]
            self.form2.editBoundary.setText(self.Boundary.Label)

    def openFileDEM(self):
        filters = "Esri ASC (*.asc);;CSV (*.csv);;All files (*.*)"
        filename = QtGui.QFileDialog.getOpenFileName(None,
                                                    "Open DEM,",
                                                    "",
                                                    filters)
        self.filename = filename[0]
        self.form1.editDEM.setText(filename[0])

    def mainToggle(self, radiobox):
        if radiobox is self.form1.radio1:
            self.select = 0
            self.form1.gbLocalFile.setVisible(True)
        elif radiobox is self.form1.radio2:
            self.select = 1
            self.form1.gbLocalFile.setVisible(True)

    def accept(self):
        from datetime import datetime
        starttime = datetime.now()

        site = PVPlantSite.get()

        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups
        except:
            PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
            PointGroups.Label = "Point Groups"

        PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
        PointGroup.Label = "Land_Grid_Points"
        FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
        PointObject = PointGroup.Points.copy()

        if self.select == 0:    # Google or bing or ...
            #for item in self.obj:
                #if self.groupbox.isChecked:break
            resol = FreeCAD.Units.Quantity(self.valueResolution.text()).Value
            Site = FreeCAD.ActiveDocument.Site
            pts = getGridElevationFromBing(self.obj, Site.Latitude, Site.Longitude, resol)
            PointObject.addPoints(pts)
            PointGroup.Points = PointObject

        else:
            if self.filename == "":
                return

            if self.select == 1: # DEM.
                import numpy as np
                root, extension = os.path.splitext(self.filename)

                if extension.lower() == ".asc":
                    grid_space = 1

                    file = open(self.filename, "r")
                    templist = [line.split() for line in file.readlines()]
                    file.close()
                    del file

                    # Read meta data:
                    meta = templist[0:6]
                    nx = int(meta[0][1])                        # NCOLS
                    ny = int(meta[1][1])                        # NROWS
                    xllcorner = round(float(meta[2][1]), 3)     # XLLCENTER
                    yllcorner = round(float(meta[3][1]), 3)     # YLLCENTER
                    cellsize = round(float(meta[4][1]), 3)      # CELLSIZE
                    nodata_value = float(meta[5][1])            # NODATA_VALUE

                    # set coarse_factor
                    coarse_factor = max(round(grid_space / cellsize), 1)

                    # Get z values
                    templist = templist[6:(6 + ny)]
                    templist = [templist[i][0::coarse_factor] for i in np.arange(0, len(templist), coarse_factor)]
                    datavals = np.array(templist).astype(float)
                    templist.clear()

                    # create xy coordinates
                    offset = site.Origin / 1000
                    x = cellsize * np.arange(nx)[0::coarse_factor] + xllcorner - offset.x
                    y = cellsize * np.arange(ny)[-1::-1][0::coarse_factor] + yllcorner - offset.y

                    if self.Boundary:
                        inc_x = self.Boundary.Shape.BoundBox.XLength * 0.05
                        inc_y = self.Boundary.Shape.BoundBox.YLength * 0.05

                        min_x = 0
                        max_x = 0

                        comp = (self.Boundary.Shape.BoundBox.XMin - inc_x) / 1000
                        for i in range(nx):
                            if x[i] > comp:
                                min_x = i - 1
                                break
                        comp = (self.Boundary.Shape.BoundBox.XMax + inc_x) / 1000
                        for i in range(min_x, nx):
                            if x[i] > comp:
                                max_x = i
                                break

                        min_y = 0
                        max_y = 0

                        comp = (self.Boundary.Shape.BoundBox.YMax + inc_y) / 1000
                        for i in range(ny):
                            if y[i] < comp:
                                max_y = i
                                break
                        comp = (self.Boundary.Shape.BoundBox.YMin - inc_y) / 1000
                        for i in range(max_y, ny):
                            if y[i] < comp:
                                min_y = i
                                break

                        x = x[min_x:max_x]
                        y = y[max_y:min_y]
                        datavals = datavals[max_y:min_y, min_x:max_x]

                    pts = []
                    if True: # faster but more memory 46s - 4,25 gb
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

                    else:   # 51s 3,2 gb
                        createmesh = True
                        if createmesh:
                            import Part, Draft, DraftGeomUtils

                            lines=[]
                            for j in range(len(y)):
                                edges = []
                                for i in range(0, len(x) - 1):
                                    ed = Part.makeLine(FreeCAD.Vector(x[i], y[j], datavals[j][i]) * 1000,
                                                       FreeCAD.Vector(x[i + 1], y[j], datavals[j][i + 1]) * 1000)
                                    edges.append(ed)

                                #bspline = Draft.makeBSpline(pts)
                                #bspline.ViewObject.hide()
                                line = Part.Wire(edges)
                                lines.append(line)

                            '''
                            for i in range(0, len(bsplines), 100):
                                p = Part.makeLoft(bsplines[i:i + 100], False, False, False)
                                Part.show(p)
                            '''
                            p = Part.makeLoft(lines, False, True, False)
                            p = Part.Solid(p)
                            Part.show(p)

                        else:
                            pts = []
                            for j in range(ny):
                                for i in range(nx):
                                    pts.append(FreeCAD.Vector(x[i], y[j], datavals[j][i]) * 1000)


                    PointObject.addPoints(pts)
                    PointGroup.Points = PointObject
                    pts.clear()

                elif extension.lower() == ".csv" or extension.lower() == ".txt":  # x, y, z from gps
                    import csv
                    import numpy as np
                    import matplotlib.mlab as ml

                    import scipy as sp
                    import scipy.interpolate

                    x=[]
                    y=[]
                    z=[]
                    # todo: dar la opción de qué delimitador usar
                    delim = ';' if extension.lower() == "csv" else ' '
                    with open(self.filename, newline='') as csvfile:
                        spamreader = csv.reader(csvfile, delimiter = delim,
                                                skipinitialspace=True)
                        for row in spamreader:
                            x.append(float(row[1]))
                            y.append(float(row[2]))
                            z.append(float(row[3]))

                    #prueba:
                    pts = []
                    for i, point in enumerate(x):
                        pts.append(FreeCAD.Vector(x[i] * 1000, y[i] * 1000, z[i] * 1000))

                    PointObject.addPoints(pts)
                    PointGroup.Points = PointObject
                    return


                    x = np.array(x)
                    y = np.array(y)
                    z = np.array(z)
                    spline = sp.interpolate.Rbf(x, y, z, function='thin-plate')

                    xi = np.linspace(min(x), max(x), int((min(x) + max(x)) / 10000))
                    yi = np.linspace(min(y), max(y), int((min(y) + max(y)) / 10000))
                    X, Y = np.meshgrid(xi, yi)
                    Z = spline(X, Y)

                    xx = X.flatten()
                    yy = Y.flatten()
                    zz = Z.flatten()

                    i = 0
                    pts = []
                    for point in xx:
                        pts.append(FreeCAD.Vector(xx[i] * 1000, yy[i] * 1000, zz[i] * 1000))
                        i += 1

                    PointObject.addPoints(pts)
                    PointGroup.Points = PointObject

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()
        print("tiempo: ", datetime.now() - starttime)

    def reject(self):
        FreeCADGui.Control.closeDialog()

## Comandos -----------------------------------------------------------------------------------------------------------
class CommandImportPoints:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "cloud.svg")),
                'MenuText': QT_TRANSLATE_NOOP("PVPlant", "Import Grid"),
                'Accel': "B, U",
                'ToolTip': QT_TRANSLATE_NOOP("PVPlant", "Creates a cloud of points.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _ImportPointsTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)

if FreeCAD.GuiUp:
    class CommandPointsGroup:

        def GetCommands(self):
            return tuple(['ImportPoints'
                          ])
        def GetResources(self):
            return { 'MenuText': QT_TRANSLATE_NOOP("",'Cloud of Points'),
                     'ToolTip': QT_TRANSLATE_NOOP("",'Cloud of Points')
                   }
        def IsActive(self):
            return not FreeCAD.ActiveDocument is None

    FreeCADGui.addCommand('ImportPoints', CommandImportPoints())
    FreeCADGui.addCommand('PointsGroup', CommandPointsGroup())

