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
import utm

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from PySide.QtCore import QT_TRANSLATE_NOOP
    from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
    from PySide2.QtWebChannel import QWebChannel
    import os
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond

from PVPlantResources import DirIcons as DirIcons
from PVPlantResources import DirResources as DirResources

class MapWindow(QtGui.QWidget):
    def __init__(self, WinTitle="MapWindow"):
        super(MapWindow, self).__init__()
        self.raise_()
        self.lat = 0
        self.lon = 0
        self.WinTitle = WinTitle

        self.setupUi()
        self.show()

    def setupUi(self):
        self.resize(1200, 800)
        self.setWindowTitle(self.WinTitle)
        self.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "Location.svg")))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)

        LeftWidget = QtGui.QWidget(self)
        LeftLayout = QtGui.QVBoxLayout(LeftWidget)
        LeftWidget.setLayout(LeftLayout)
        LeftLayout.setContentsMargins(0, 0, 0, 0)

        RightWidget = QtGui.QWidget(self)
        RightWidget.setFixedWidth(350)
        RightLayout = QtGui.QVBoxLayout(RightWidget)
        RightWidget.setLayout(RightLayout)
        RightLayout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(LeftWidget)
        self.layout.addWidget(RightWidget)

        # Left Widgets:
        # -- Search Bar:
        self.valueSearch = QtGui.QLineEdit(self)
        self.valueSearch.setPlaceholderText("Search")
        self.valueSearch.returnPressed.connect(self.GeoCoder)

        searchbutton = QtGui.QPushButton('Search')
        searchbutton.setFixedWidth(80)
        searchbutton.clicked.connect(self.onSearch)

        SearchBarLayout = QtGui.QHBoxLayout(self)
        SearchBarLayout.addWidget(self.valueSearch)
        SearchBarLayout.addWidget(searchbutton)
        LeftLayout.addLayout(SearchBarLayout)

        # -- Webbroser:
        self.view = QWebEngineView()
        self.channel = QWebChannel(self.view.page())
        self.view.page().setWebChannel(self.channel)
        self.channel.registerObject("MyApp", self)
        file = os.path.join(DirResources, "webs", "main.html")
        self.view.page().loadFinished.connect(self.onLoadFinished)
        self.view.page().load(QtCore.QUrl.fromLocalFile(file))
        LeftLayout.addWidget(self.view)
        # self.layout.addWidget(self.view, 1, 0, 1, 3)

        # -- Latitud y longitud:
        self.labelCoordinates = QtGui.QLabel()
        self.labelCoordinates.setFixedHeight(21)
        LeftLayout.addWidget(self.labelCoordinates)
        # self.layout.addWidget(self.labelCoordinates, 2, 0, 1, 3)

        # Right Widgets:
        labelKMZ = QtGui.QLabel()
        labelKMZ.setText("Cargar un archivo KMZ/KML:")
        self.kmlButton = QtGui.QPushButton()
        self.kmlButton.setFixedSize(32, 32)
        self.kmlButton.setIcon(QtGui.QIcon(os.path.join(DirIcons, "googleearth.svg")))
        widget = QtGui.QWidget(self)
        layout = QtGui.QHBoxLayout(widget)
        widget.setLayout(layout)
        layout.addWidget(labelKMZ)
        layout.addWidget(self.kmlButton)
        RightLayout.addWidget(widget)

        # -----------------------
        self.groupbox = QtGui.QGroupBox("Importar datos desde:")
        self.groupbox.setCheckable(True)
        self.groupbox.setChecked(True)
        radio1 = QtGui.QRadioButton("Google Elevation")
        radio2 = QtGui.QRadioButton("Nube de Puntos")
        radio3 = QtGui.QRadioButton("Datos GPS")
        radio1.setChecked(True)

        # buttonDialog = QtGui.QPushButton('...')
        # buttonDialog.setEnabled(False)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        # vbox.addStretch(1)

        # vbox = QtGui.QGridLayout(groupbox)
        # vbox.addWidget(radio1, 0, 0, 1, 1)
        # vbox.addWidget(radio2, 1, 0, 1, 1)
        # vbox.addWidget(radio3, 2, 0, 1, 1)
        # vbox.addWidget(buttonDialog, 3, 0, 1, 1)

        self.groupbox.setLayout(vbox)
        RightLayout.addWidget(self.groupbox)
        # ------------------------

        verticalSpacer = QtGui.QSpacerItem(20, 48, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        RightLayout.addItem(verticalSpacer)

        self.bAccept = QtGui.QPushButton('Accept')
        self.bAccept.clicked.connect(self.onAcceptClick)
        RightLayout.addWidget(self.bAccept)

        # signals/slots
        QtCore.QObject.connect(self.kmlButton, QtCore.SIGNAL("clicked()"), self.importKML)


    def onSearch(self):
        frame = self.view.page()
        frame.runJavaScript(
            "MyApp.georeference(drawnItems.getBounds().getCenter().lat, drawnItems.getBounds().getCenter().lng);" \
            "var data = drawnItems.toGeoJSON();" \
            "var convertedData = JSON.stringify(data);" \
            "MyApp.shapes(convertedData);"
        )

    def onAcceptClick(self):
        frame = self.view.page()
        frame.runJavaScript(
            "MyApp.georeference(drawnItems.getBounds().getCenter().lat, drawnItems.getBounds().getCenter().lng);" \
            "var data = drawnItems.toGeoJSON();" \
            "var convertedData = JSON.stringify(data);" \
            "MyApp.shapes(convertedData);"
        )
        self.close()

    def onLoadFinished(self):
        file = os.path.join(DirResources, "webs", "map.js")
        with open(file, 'r') as f:
            frame = self.view.page()
            frame.runJavaScript(f.read())

    @QtCore.Slot(float, float)
    def onMapMove(self, lat, lng):
        self.lat = lat
        self.lon = lng
        x, y, zone_number, zone_letter = utm.from_latlon(lat, lng)
        self.labelCoordinates.setText('Longitud: {:.5f}, Latitud: {:.5f}'.format(lng, lat) +
                                      '  |  UTM: ' + str(zone_number) + zone_letter +
                                      ', {:.5f}m E, {:.5f}m N'.format(x, y))

    @QtCore.Slot(float, float)
    def georeference(self, lat, lon):
        import PVPlantSite

        Site = PVPlantSite.get()
        Site.Proxy.setLatLon(lat, lon)

    @QtCore.Slot(str)
    def shapes(self, drawnItems):
        '''
        Punto:
        {"geometry": {"coordinates": [-5.756493, 39.961195], "type": "Point"}, "properties": {}, "type": "Feature"}

        Poligon:
        {"geometry": {"coordinates": [[[-5.758424, 39.961645], [-5.758424, 39.961645], [-5.75808, 39.952006], [-5.75808, 39.952006], [-5.749412, 39.952894], [-5.749412, 39.952894], [-5.754304, 39.9625], [-5.754304, 39.9625], [-5.758424, 39.961645]]], "type": "Polygon"}, "properties": {}, "type": "Feature"}
        '''

        import geojson
        import PVPlantImportGrid as ImportElevation

        items = geojson.loads(drawnItems)
        count_points = 0
        count_polygons = 0
        for item in items['features']:

            # 1. if the feature is a Point:
            if item['geometry']['type'] == "Point":
                count_points += 1
                coord = item['geometry']['coordinates']
                point = FreeCAD.Vector(coord[0], coord[1])

            # 2. if the feature is a Polygon:
            if item['geometry']['type'] == "Polygon":
                count_polygons += 1
                pts = []
                for cords in item['geometry']['coordinates'][0]:
                    pts.append(ImportElevation.getSinglePointElevationFromBing(cords[1], cords[0]))

                # Draw polygons/boundary:
                Wire = Draft.makeWire(pts, closed=True, face=False, name="Polygon")
                Wire.Label = "Polygon"
                Draft.autogroup(Wire)

        FreeCAD.activeDocument().recompute()
        FreeCADGui.updateGui()
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def panMap(self, lng, lat, geometry=""):
        frame = self.view.page()
        geo1 = '{geo}'.format(lt=lat, lg=lng, geo=geometry)
        geo1 = geo1.replace("'", "")
        geo1 = geo1.replace("northeast", "_northEast")
        geo1 = geo1.replace("southwest", "_southWest")
        geo1 = 'map.panTo(L.latLng({lt}, {lg})); map.fitBounds({geo});'.format(lt=lat, lg=lng, geo=geo1)
        frame.runJavaScript(geo1)

    def GeoCoder(self): # TODO:
        import urllib.request, json
        base = r"https://maps.googleapis.com/maps/api/geocode/json?"
        addP = "address=" + self.valueSearch.text().replace(" ", "+")
        GeoUrl = base + addP + "&key=" + "AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"
        print(GeoUrl)
        response = urllib.request.urlopen(GeoUrl)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)
        if jsonData['status'] == 'OK':
            resu = jsonData['results'][0]
            finList = [resu['formatted_address'], resu['geometry']['location']['lat'],
                       resu['geometry']['location']['lng'], resu['geometry']['bounds']]
            self.valueSearch.setText(finList[0])
            self.panMap(finList[2], finList[1], finList[3])

        else:
            finList = [None, None, None]

    def importKML(self):
        file = QtGui.QFileDialog.getOpenFileName(None, "FileDialog", "", "Google Earth (*.kml *.kmz)")[0]

        if file != "":
            import os.path
            extension = os.path.splitext(file)[1]

            doc = None
            if extension == '.kmz':
                from zipfile import ZipFile
                kmz = ZipFile(file, 'r')
                myfile = kmz.open('doc.kml', 'r')
                doc = myfile.read().decode('utf-8')
            else:
                myfile = open(file, 'rt', encoding="utf-8")
                doc = myfile.read()
                # import codecs
                # with codecs.open(file, 'r', 'utf-8') as myfile:
                # with open(file, 'rt', encoding="utf-8") as myfile:
                # print (myfile)
                # myfile.seek(0)
                # doc = myfile.read()
                # from pykml import parser
                # doc = parser.parse(myfile)
                # root = parser.fromstring(doc)

            print(doc)

            frame = self.view.page()
            # code = "var runLayer = omnivore.kml('file:///" + file + "')" \
            #                                    ".on('ready', function() {" \
            #                                    "map.fitBounds(runLayer.getBounds());" \
            #                                    "})" \
            #                                    ".addTo(map);"

            # omnivore.kml.parse(text).addTo(map);
            code = "var runLayer = omnivore.kml.parse('" + doc + "')" \
                                                                 ".on('ready', function() {" \
                                                                 "map.fitBounds(runLayer.getBounds());" \
                                                                 "})" \
                                                                 ".addTo(map);"

            code = "var runLayer = omnivore" \
                   ".kml('https://storage.googleapis.com/cfb-documents/cityscape-4.kml')" \
                   ".on('ready', function(event) {" \
                   "console.clear();" \
                   "map.fitBounds(event.target.getBounds());" \
                   "console.log(event.target.getBounds());" \
                   "})" \
                   ".addTo(drawnItems);"
            print(code)
            frame.runJavaScript(code)

class _CommandPVPlantGeoreferencing:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "Location.svg")),
                'Accel': "G, R",
                'MenuText': QT_TRANSLATE_NOOP("Georeferencing","Georeferencing"),
                'ToolTip': QT_TRANSLATE_NOOP("Georeferencing","Referenciar el lugar")}

    def Activated(self):
        self.form = MapWindow()
        self.form.show()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantGeoreferencing',_CommandPVPlantGeoreferencing())