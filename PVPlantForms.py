
__title__="FreeCAD Precast concrete module"
__author__ = "Javier Brana"
__url__ = ""


import FreeCAD, Draft, Part
import PVPlantRack
from FreeCAD import Vector

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


__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")


class _ModuleTaskPanel:
    def __init__(self, obj = None):

        print(obj)
        if obj is not None:
            self.obj = obj
        else:
            a = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Rack")
            self.obj = PVPlantRack._Rack(a)
            PVPlantRack._ViewProviderRack(a.ViewObject)

        self.ModuleLength = 0
        self.ModuleWidth = 0
        self.ModuleHeight = 0
        self.ModuleFrame = 0
        self.ModuleColor = 0

        self.form = QtGui.QWidget()
        self.form.setObjectName("TaskPanel")
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "Module.svg")))

        self.grid = QtGui.QGridLayout(self.form)
        self.SlabTypes = ["Champagne","Hat"]

        # image display
        self.preview = QtSvg.QSvgWidget(os.path.join(DirImages, "Module.svg"))
        self.preview.setMaximumWidth(200)
        self.preview.setMinimumHeight(120)
        self.grid.addWidget(self.preview, self.grid.rowCount() - 1, 0, 1, 1)

        # parameters
        self.labelModule = QtGui.QLabel()
        self.valueModule = QtGui.QComboBox()
        self.valueModule.addItems(self.SlabTypes)
        self.valueModule.setCurrentIndex(0)
        self.grid.addWidget(self.labelModule, self.grid.rowCount(),0,1,1)
        self.grid.addWidget(self.valueModule, self.grid.rowCount() -1,1,1,1)

        self.labelModuleLength = QtGui.QLabel()
        self.valueModuleLength = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueModuleLength.setText(FreeCAD.Units.Quantity(1956,FreeCAD.Units.Length).UserString)
        self.grid.addWidget(self.labelModuleLength, self.grid.rowCount(),0,1,1)
        self.grid.addWidget(self.valueModuleLength, self.grid.rowCount() - 1,1,1,1)

        self.labelModuleHeight = QtGui.QLabel()
        self.valueModuleHeight = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueModuleHeight.setText(FreeCAD.Units.Quantity(992,FreeCAD.Units.Length).UserString)
        self.grid.addWidget(self.labelModuleHeight, self.grid.rowCount(),0,1,1)
        self.grid.addWidget(self.valueModuleHeight, self.grid.rowCount() - 1,1,1,1)

        self.labelModuleWidth = QtGui.QLabel()
        self.valueModuleWidth = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueModuleWidth.setText(FreeCAD.Units.Quantity(40,FreeCAD.Units.Length).UserString)
        self.grid.addWidget(self.labelModuleWidth, self.grid.rowCount(),0,1,1)
        self.grid.addWidget(self.valueModuleWidth, self.grid.rowCount() - 1,1,1,1)

        self.labelModuleFrame = QtGui.QLabel()
        self.valueModuleFrame = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleFrame, self.grid.rowCount(),0,1,1)
        self.grid.addWidget(self.valueModuleFrame, self.grid.rowCount() - 1,1,1,1)

        self.labelModuleColor = QtGui.QLabel()
        self.valueModuleColor = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        #self.grid.addWidget(self.labelModuleColor, self.grid.rowCount(),0,1,1)
        #self.grid.addWidget(self.valueModuleColor, self.grid.rowCount() - 1,1,1,1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)


        # -------------------------------------------------------------------------------------------------------------
        # Rack part
        # -------------------------------------------------------------------------------------------------------------
        self.ModuleOrientation = ["Portrait", "Landscape"]
        self.RackType = ["Fija", "1 Eje", "2 Ejes"]

        # Title
        self.labelModules = QtGui.QLabel()
        self.grid.addWidget(self.labelModules, self.grid.rowCount(), 0, 1, -1)

        # image display
        self.preview = QtSvg.QSvgWidget(":/ui/ParametersDent.svg")
        self.preview.setMaximumWidth(200)
        self.preview.setMinimumHeight(120)
        self.grid.addWidget(self.preview, self.grid.rowCount(), 0, 1, -1)

        self.labelModuleOrientation = QtGui.QLabel()
        self.valueModuleOrientation = QtGui.QComboBox()
        self.valueModuleOrientation.addItems(self.ModuleOrientation)
        self.valueModuleOrientation.setCurrentIndex(0)
        self.grid.addWidget(self.labelModuleOrientation, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueModuleOrientation, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelModuleGapX = QtGui.QLabel()
        self.valueModuleGapX = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleGapX, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueModuleGapX, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelModuleGapY = QtGui.QLabel()
        self.valueModuleGapY = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleGapY, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueModuleGapY, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelModuleRows = QtGui.QLabel()
        self.valueModuleRows = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleRows, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueModuleRows, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelModuleCols = QtGui.QLabel()
        self.valueModuleCols = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleCols, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueModuleCols, self.grid.rowCount() - 1, 1, 1, 1)


        # Configuración de la estructura ------------------------------------------------------------------------------
        self.line2 = QtGui.QFrame()
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line2, self.grid.rowCount(), 0, 1, -1)

        # Title
        self.labelRack = QtGui.QLabel()
        self.grid.addWidget(self.labelRack, self.grid.rowCount(), 0, 1, 1)

        # image display
        self.preview = QtSvg.QSvgWidget(":/ui/ParametersDent.svg")
        self.preview.setMaximumWidth(200)
        self.preview.setMinimumHeight(120)
        self.grid.addWidget(self.preview, self.grid.rowCount(), 0, 1, -1)

        self.labelRackType = QtGui.QLabel()
        self.valueRackType = QtGui.QComboBox()
        self.valueRackType.addItems(self.RackType)
        self.valueRackType.setCurrentIndex(0)
        self.grid.addWidget(self.labelRackType, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueRackType, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelLevel = QtGui.QLabel()
        self.valueLevel = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelLevel, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueLevel, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelOffset = QtGui.QLabel()
        self.valueOffset = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelOffset, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueOffset, self.grid.rowCount() - 1, 1, 1, 1)

        self.retranslateUi(self.form)

        self.part = FreeCAD.ActiveDocument.addObject('App::Part', 'Tracker')
        self.pole = FreeCAD.ActiveDocument.addObject("Part::Box", "Pole")
        self.poles = Draft.makeArray(self.pole, FreeCAD.Vector(1, 0, 0), FreeCAD.Vector(0, 1, 0), 2, 2)
        self.partStructure = FreeCAD.ActiveDocument.addObject('App::Part', 'Structure')
        self.Module = FreeCAD.ActiveDocument.addObject("Part::Box", "Module")
        self.ModuleArray = Draft.makeArray(self.Module, FreeCAD.Vector(1, 0, 0), FreeCAD.Vector(0, 1, 0), 2, 2)
        self.axe = FreeCAD.ActiveDocument.addObject("Part::Box", "Axe")



        # signals/slots
        QtCore.QObject.connect(self.valueModuleLength,QtCore.SIGNAL("valueChanged(double)"),self.setModuleLength)
        QtCore.QObject.connect(self.valueModuleWidth,QtCore.SIGNAL("valueChanged(double)"),self.setModuleWidth)
        QtCore.QObject.connect(self.valueModuleHeight,QtCore.SIGNAL("valueChanged(double)"),self.setModuleHeight)
        QtCore.QObject.connect(self.valueModuleFrame, QtCore.SIGNAL("valueChanged(double)"), self.setModuleFrame)
        QtCore.QObject.connect(self.valueModuleColor, QtCore.SIGNAL("valueChanged(double)"), self.setModuleColor)
        #QtCore.QObject.connect(self.valueModuleGapX, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapX)
        #QtCore.QObject.connect(self.valueModuleGapY, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapY)

        self.drawmodule()

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

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleLength"] = self.ModuleLength
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleHeight"] = self.ModuleHeight
        return d

    def setModuleLength(self,value):
        self.ModuleLength = value
        self.drawmodule()

    def setModuleWidth(self,value):
        self.ModuleWidth = value
        self.drawmodule()

    def setModuleHeight(self,value):
        self.ModuleHeight = value
        self.drawmodule()

    def setModuleFrame(self,value):
        self.ModuleFrame = value
        self.drawmodule()

    def setModuleColor(self,value):
        self.ModuleColor = value
        self.drawmodule()

    def drawmodule(self):
        #import PVPlantModule
        #PVPlantModule.makeModule()
        #FreeCADGui.addModule("PVPlantModule")
        #FreeCADGui.doCommand('s = PVPlantModule.makeModule()')

        # Part Tracker:
        self.part.Label = 'Tracker'

        # Poles:
        self.pole.Label = "Pole"
        self.pole.Length = 150
        self.pole.Width = 150
        self.pole.Height = 3100
        self.pole.Placement.Base.y = - self.pole.Width / 2
        #self.pole.setExpression("Placement.Base.x", u'ArrayOfModules.Placement.Base.x')
        #self.pole.setExpression("Placement.Base.y", u'(ArrayOfModules.NumberY * Module.Width + (ArrayOfModules.NumberY - 1) * 40mm) / 2mm - Axe.Width / 2mm')
        self.part.addObject(self.pole)

        # Array of Poles:
        self.poles.Label = "ArrayOfPoles"
        Draft.autogroup(self.poles)
        self.poles.NumberX = 7
        self.poles.NumberY = 1
        self.poles.NumberZ = 1
        #self.poles.setExpression('IntervalX.x', u'(Axe.Length - Pole.Length) / 6')
        self.poles.IntervalX.x = 7000
        self.poles.Placement.Base.z = -1450
        self.poles.Placement.Base.x = 1600
        self.part.addObject(self.poles)

        # Part Structure:

        self.partStructure.Label = 'Structure'
        self.partStructure.Placement.Base.z = 1894
        self.part.addObject(self.partStructure)

        # Module:
        self.Module.Label = "Module"
        self.Module.Length = self.ModuleLength
        self.Module.Width = self.ModuleWidth
        self.Module.Height = self.ModuleHeight

        # Array of Modules:
        self.ModuleArray.Label = "ArrayOfModules"
        Draft.autogroup(self.ModuleArray)
        self.ModuleArray.Placement.Base.z = 75 + 90
        self.ModuleArray.NumberX = 45
        self.ModuleArray.NumberY = 2
        self.ModuleArray.setExpression('IntervalX.x', u'Module.Length + 40 mm')
        self.ModuleArray.setExpression('IntervalY.y', u'Module.Width + 40 mm')
        self.partStructure.addObject(self.ModuleArray)

        self.Module.Placement.Base.y = -(self.ModuleArray.IntervalY.y * self.ModuleArray.NumberY - 40) / 2

        # Eje:
        self.axe.Label = "Axe"
        self.axe.setExpression('Length', u'ArrayOfModules.NumberX * Module.Length + (ArrayOfModules.NumberX - 1) * 40mm + 140mm')
        self.axe.Width = 150
        self.axe.Height = 150
        #self.axe.setExpression("Placement.Base.x", u'ArrayOfModules.Placement.Base.x')
        #self.axe.setExpression("Placement.Base.y", u'(ArrayOfModules.NumberY * Module.Width + (ArrayOfModules.NumberY - 1) * 40mm) / 2mm - Axe.Width / 2mm')
        self.axe.Placement.Base.x = -70
        self.axe.Placement.Base.y = -self.axe.Width/2
        self.axe.Placement.Base.z = -self.axe.Height/2
        self.partStructure.addObject(self.axe)

        #FreeCAD.ActiveDocument.recompute()


    def accept(self):
        #FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        #self.part = FreeCAD.ActiveDocument.addObject('App::Part', 'Tracker')
        #self.pole = FreeCAD.ActiveDocument.addObject("Part::Box", "Pole")
        #self.poles = Draft.makeArray(self.pole, FreeCAD.Vector(1, 0, 0), FreeCAD.Vector(0, 1, 0), 2, 2)
        #self.partStructure = FreeCAD.ActiveDocument.addObject('App::Part', 'Structure')
        #self.Module = FreeCAD.ActiveDocument.addObject("Part::Box", "Module")
        #self.ModuleArray = Draft.makeArray(self.Module, FreeCAD.Vector(1, 0, 0), FreeCAD.Vector(0, 1, 0), 2, 2)
        #self.axe = FreeCAD.ActiveDocument.addObject("Part::Box", "Axe")

        #App.getDocument("Sin_nombre").getObject("Tracker").removeObjectsFromDocument()
        #App.getDocument("Sin_nombre").removeObject("Tracker")
        FreeCAD.ActiveDocument.removeObject(self.part.Name)
        return True


class PlacementTaskPanel(QtGui.QWidget):

    '''The TaskPanel for dent creation'''

    def __init__(self):
        super(PlacementTaskPanel, self).__init__()
        self.raise_()
        self.setupUi()
        self.show()

    def setupUi(self):
        from QtCore import QEventLoop
        self.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "Placement.svg")))

        self.grid = QtGui.QGridLayout(self)
        self.ModuleOrientation = ["Portrait", "Landscape"]
        self.RackType = ["Fija","1 Eje", "2 Ejes"]

        # image display
        self.preview = QtSvg.QSvgWidget(":/ui/ParametersDent.svg")
        self.preview.setMaximumWidth(200)
        self.preview.setMinimumHeight(120)
        self.grid.addWidget(self.preview,0,0,1,2)

        # parameters
        self.labelModules = QtGui.QLabel()
        self.grid.addWidget(self.labelModules, 1, 0, 1, 1)

        self.labelModuleOrientation = QtGui.QLabel()
        self.valueModuleOrientation = QtGui.QComboBox()
        self.valueModuleOrientation.addItems(self.ModuleOrientation)
        self.valueModuleOrientation.setCurrentIndex(0)
        self.grid.addWidget(self.labelModuleOrientation,2,0,1,1)
        self.grid.addWidget(self.valueModuleOrientation,2,1,1,1)

        self.labelModuleGapX = QtGui.QLabel()
        self.valueModuleGapX = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleGapX,4,0,1,1)
        self.grid.addWidget(self.valueModuleGapX,4,1,1,1)

        self.labelModuleGapY = QtGui.QLabel()
        self.valueModuleGapY = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleGapY,5,0,1,1)
        self.grid.addWidget(self.valueModuleGapY,5,1,1,1)

        self.labelModuleRows = QtGui.QLabel()
        self.valueModuleRows = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleRows,6,0,1,1)
        self.grid.addWidget(self.valueModuleRows,6,1,1,1)

        self.labelModuleCols = QtGui.QLabel()
        self.valueModuleCols = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelModuleCols,7,0,1,1)
        self.grid.addWidget(self.valueModuleCols,7,1,1,1)

        self.labelRack = QtGui.QLabel()
        self.grid.addWidget(self.labelRack, 8, 0, 1, 1)

        self.labelRackType = QtGui.QLabel()
        self.valueRackType = QtGui.QComboBox()
        self.valueRackType.addItems(self.RackType)
        self.valueRackType.setCurrentIndex(0)
        self.grid.addWidget(self.labelRackType,9,0,1,1)
        self.grid.addWidget(self.valueRackType,9,1,1,1)

        self.labelLevel = QtGui.QLabel()
        self.valueLevel = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelLevel,10,0,1,1)
        self.grid.addWidget(self.valueLevel,10,1,1,1)

        self.labelOffset = QtGui.QLabel()
        self.valueOffset = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.grid.addWidget(self.labelOffset,11,0,1,1)
        self.grid.addWidget(self.valueOffset,11,1,1,1)

        # signals/slots
        QtCore.QObject.connect(self.valueModuleGapX,QtCore.SIGNAL("valueChanged(double)"),self.setModuleGapX)
        QtCore.QObject.connect(self.valueModuleGapY,QtCore.SIGNAL("valueChanged(double)"),self.setModuleGapY)
        self.retranslateUi()

    def setModuleGapX(self,value):
        self.Length = value

    def setModuleGapY(self,value):
        self.Width = value

    def retranslateUi(self):
        self.setWindowTitle("Configuracion del Rack")
        self.labelModules.setText(QtGui.QApplication.translate("Arch", "Colocacion de los Modulos", None))
        self.labelModuleOrientation.setText(QtGui.QApplication.translate("Arch", "Orientacion del modulo:", None))
        self.labelModuleGapX.setText(QtGui.QApplication.translate("Arch", "Separacion Horizontal (mm):", None))
        self.labelModuleGapY.setText(QtGui.QApplication.translate("Arch", "Separacion Vertical (mm):", None))
        self.labelModuleRows.setText(QtGui.QApplication.translate("Arch", "Filas de modulos:", None))
        self.labelModuleCols.setText(QtGui.QApplication.translate("Arch", "Columnas de modulos:", None))
        self.labelRack.setText(QtGui.QApplication.translate("Arch", "Configuracion de la estructura", None))
        self.labelRackType.setText(QtGui.QApplication.translate("Arch", "Tipo de estructura:", None))
        self.labelOffset.setText(QtGui.QApplication.translate("Arch", "Offset", None))



class MapWindow(QtGui.QWidget):
    def __init__(self, WinTitle = "MapWindow"):
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
        #self.layout.addWidget(self.view, 1, 0, 1, 3)

        # -- Latitud y longitud:
        self.labelCoordinates = QtGui.QLabel()
        self.labelCoordinates.setFixedHeight(21)
        LeftLayout.addWidget(self.labelCoordinates)
        #self.layout.addWidget(self.labelCoordinates, 2, 0, 1, 3)

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

        #-----------------------
        self.groupbox = QtGui.QGroupBox("Importar datos desde:")
        self.groupbox.setCheckable(True)
        self.groupbox.setChecked(True)
        radio1 = QtGui.QRadioButton("Google Elevation")
        radio2 = QtGui.QRadioButton("Nube de Puntos")
        radio3 = QtGui.QRadioButton("Datos GPS")
        radio1.setChecked(True)

        #buttonDialog = QtGui.QPushButton('...')
        #buttonDialog.setEnabled(False)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        #vbox.addStretch(1)

        #vbox = QtGui.QGridLayout(groupbox)
        #vbox.addWidget(radio1, 0, 0, 1, 1)
        #vbox.addWidget(radio2, 1, 0, 1, 1)
        #vbox.addWidget(radio3, 2, 0, 1, 1)
        #vbox.addWidget(buttonDialog, 3, 0, 1, 1)

        self.groupbox.setLayout(vbox)
        RightLayout.addWidget(self.groupbox)
        #------------------------

        verticalSpacer = QtGui.QSpacerItem(20, 48, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        RightLayout.addItem(verticalSpacer)

        self.bAccept = QtGui.QPushButton('Accept')
        RightLayout.addWidget(self.bAccept)

        # signals/slots
        QtCore.QObject.connect(self.kmlButton, QtCore.SIGNAL("clicked()"), self.importKML)
        QtCore.QObject.connect(self.bAccept, QtCore.SIGNAL("clicked()"), self.OnAcceptClick)
        #QtCore.QObject.connect(searchbutton, QtCore.SIGNAL("clicked()"), self.GeoCoder)

    def OnAcceptClick(self):
        frame = self.view.page()
        frame.runJavaScript("MyApp.georeference(drawnItems.getBounds().getCenter().lat, drawnItems.getBounds().getCenter().lng);" \
                            "var data = drawnItems.toGeoJSON();" \
                            "var convertedData = JSON.stringify(data);" \
                             "MyApp.shapes(convertedData);")

    def onLoadFinished(self):
        #self.init_loop.quit
        file = os.path.join(DirResources, "webs", "map.js")
        with open(file, 'r') as f:
            frame = self.view.page()
            frame.runJavaScript(f.read())

    @QtCore.Slot(float, float)
    def onMapMove(self, lat, lng):
        self.lat = lat
        self.lon = lng
        self.labelCoordinates.setText('Longitud: {:.5f}, Latitud: {:.5f}'.format(lng, lat))

    @QtCore.Slot(float, float)
    def georeference(self, lat, lng):

        try:
            Site = FreeCAD.ActiveDocument.Site
        except:
            import PVPlantSite
            Site = PVPlantSite.makeSite(objectslist=None, baseobj=None, name="Site")

        Site.Longitude = lng
        Site.Latitude = lat
        Site.Declination = 0

        import utm
        geo = utm.from_latlon(lat, lng)
        # result = (679434.3578335291, 4294023.585627955, 30, 'S')
        # EASTING, NORTHING, ZONE NUMBER, ZONE LETTER
        self.easting = geo[0]
        self.northing = geo[1]
        self.zoneNumber = geo[2]
        self.zoneLetrer = geo[3]

        #FreeCAD.ActiveDocument.recompute()


    @QtCore.Slot(str)
    def shapes(self, drawnItems):
        import geojson
        import PVPlantImportGrid as ImportElevation
        items = geojson.loads(drawnItems)
        
        '''
        georeferencing = ""
        for item in items['features']:
            if item['geometry']['type'] == "LineString":
                print ("")
            elif item['geometry']['type'] == "Point":
                for coo in item['geometry']['coordinates']:
                    print (coo)
                    #center = ImportElevation.getSinglePointElevation(coo[1], coo[0])
            elif item['geometry']['type'] == "Polygon":
                import utm
                for coo in item['geometry']['coordinates'][0]:
                    georeferencing = utm.from_latlon(coo[1], coo[0])
                    break
                break
        print (georeferencing)
        '''

        for item in items['features']:
            pts = []
            for coo in item['geometry']['coordinates'][0]:
                #pts.append(ImportElevation.getSinglePointElevation1(coo[1], coo[0]))
                #pts.append(ImportElevation.getSinglePointElevationUtm(coo[1], coo[0]))
                pts.append(ImportElevation.getSinglePointElevationFromBing(coo[1], coo[0]))

            # Get or create "Point_Groups".
            try:
                PointGroups = FreeCAD.ActiveDocument.Point_Groups
            except:
                PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
                PointGroups.Label = "Point Groups"

            #try:
            #    FreeCAD.ActiveDocument.Points
            #except:
            #    Points = FreeCAD.ActiveDocument.addObject('Points::Feature', "Points")
            #    PointGroups.addObject(Points)

            # Get or create "Points":
            PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
            PointGroup.Label = "Boundary_Land_Points"
            FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
            PointObject = PointGroup.Points.copy()
            PointObject.addPoints(pts)
            PointGroup.Points = PointObject

            # Draw polygons/boundary:
            Wire = Draft.makeWire(pts, closed=True, face=False)
            Wire.Label = "Land"
            Draft.autogroup(Wire)
            FreeCAD.activeDocument().recompute()

            # Import Surface: ?? cambiar para no hacerlo siempre
            PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
            PointGroup.Label = "Land_Grid_Points"
            FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
            PointObject = PointGroup.Points.copy()
            #if self.groupbox.isChecked:
            #    PointObject.addPoints(ImportElevation.getElevation1(Wire, 10))
            #    PointGroup.Points = PointObject

        FreeCADGui.updateGui()
        FreeCADGui.SendMsgToActiveView("ViewFit")

    def importFromGoogle(self):
        print("")


    def panMap(self, lng, lat, geometry = ""):
        frame = self.view.page()
        geo1 = '{geo}'.format(lt = lat, lg=lng, geo=geometry)
        geo1 = geo1.replace("'", "")
        geo1 = geo1.replace("northeast","_northEast")
        geo1 = geo1.replace("southwest", "_southWest")
        geo1 = 'map.panTo(L.latLng({lt}, {lg})); map.fitBounds({geo});'.format(lt = lat, lg=lng, geo=geo1)
        print (geo1)
        frame.runJavaScript(geo1)

    def GeoCoder(self):
        import urllib.request, json
        base = r"https://maps.googleapis.com/maps/api/geocode/json?"
        addP = "address=" + self.valueSearch.text().replace(" ", "+")
        GeoUrl = base + addP + "&key=" + "AIzaSyB07X6lowYJ-iqyPmaFJvr-6zp1J63db8U"
        response = urllib.request.urlopen(GeoUrl)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)
        if jsonData['status'] == 'OK':
            resu = jsonData['results'][0]
            finList = [resu['formatted_address'], resu['geometry']['location']['lat'],
                       resu['geometry']['location']['lng'],resu['geometry']['bounds']]
            self.valueSearch.setText(finList[0])
            self.panMap(finList[2], finList[1], finList[3])

        else:
            finList = [None, None, None]

    def importKML(self):
        file = QtGui.QFileDialog.getOpenFileName(None, "FileDialog", "", "Google Earth (*.kml *.kmz)")[0]

        if file != "":
            import os.path
            extension = os.path.splitext(file)[1]

            if extension == '.kmz':
                from zipfile import ZipFile
                kmz = ZipFile(file, 'r')
                myfile = kmz.open('doc.kml', 'r')
                doc = myfile.read().decode('utf-8')
            else:
                myfile = open(file, 'rt', encoding="utf-8")
                doc = myfile.read()
                #import codecs
                #with codecs.open(file, 'r', 'utf-8') as myfile:
                #with open(file, 'rt', encoding="utf-8") as myfile:
                    #print (myfile)
                    #myfile.seek(0)
                    #doc = myfile.read()
                    #from pykml import parser
                    #doc = parser.parse(myfile)
                    # root = parser.fromstring(doc)

            frame = self.view.page()
            #code = "var runLayer = omnivore.kml('file:///" + file + "')" \
            #                                    ".on('ready', function() {" \
            #                                    "map.fitBounds(runLayer.getBounds());" \
            #                                    "})" \
            #                                    ".addTo(map);"

            #omnivore.kml.parse(text).addTo(map);
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

