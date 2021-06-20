import FreeCAD

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from PySide.QtCore import QT_TRANSLATE_NOOP

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

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


__title__ = "PVPlat tool proyect to Mesh"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")


class _CommandToolProyectToMesh:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': 'PVPlant',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantRack", "Fixed Rack"),
                'Accel': "P, M",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantRack",
                                                    "Creates a Fixed Rack object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _ToolProyectToMesh()
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return


class _ToolProyectToMesh:
    '''The TaskPanel to setup the fence'''

    def __init__(self):

        # form: -----------------------------------------------------------------------------------
        self.formFence = QtGui.QWidget()
        self.formFence.resize(800, 640)
        self.formFence.setWindowTitle("Fence setup")
        self.formFence.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.formFence)

        # parameters
        self.labelPath = QtGui.QLabel()
        self.labelPath.setText("Recorrido:")
        self.linePath = QtGui.QLineEdit(self.formFence)
        self.linePath.setObjectName(_fromUtf8("lineEdit1"))
        self.linePath.readOnly = True
        self.grid.addWidget(self.labelPath, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.linePath, self.grid.rowCount() - 1, 1, 1, 1)

        self.buttonPathSelect = QtGui.QPushButton('Add')
        self.grid.addWidget(self.buttonPathSelect, self.grid.rowCount() - 1, 2, 1, 1)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        self.label = QtGui.QLabel()
        self.label.setText("Separación entre apoyos:")
        self.grid.addWidget(self.label, self.grid.rowCount(), 0, 1, -1)

        self.labelInterval = QtGui.QLabel()
        self.labelInterval.setText("Intervalo:")
        self.valueInterval = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueInterval.setText("4,0 m")
        self.grid.addWidget(self.labelInterval, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueInterval, self.grid.rowCount() - 1, 1, 1, 2)

        self.line1 = QtGui.QFrame()
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.grid.addWidget(self.line1, self.grid.rowCount(), 0, 1, -1)

        self.label = QtGui.QLabel()
        self.label.setText("Mayado:")
        self.grid.addWidget(self.label, self.grid.rowCount(), 0, 1, -1)

        self.labelHeight = QtGui.QLabel()
        self.labelHeight.setText("Altura:")
        self.valueHeight = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueHeight.setText("2 m")
        self.grid.addWidget(self.labelHeight, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueHeight, self.grid.rowCount() - 1, 1, 1, 2)

        self.labelOffset = QtGui.QLabel()
        self.labelOffset.setText("Separación del suelo:")
        self.valueOffset = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueOffset.setText("0 m")
        self.grid.addWidget(self.labelOffset, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueOffset, self.grid.rowCount() - 1, 1, 1, 2)

        #self.buttonPathSelect.clicked.connect(self.addPath)
        #self.valueInterval.valueChanged.connect(self.SetupGrid)
        #self.valueHeight.valueChanged.connect(self.SetupGrid)
        #self.valueDepth.valueChanged.connect(self.SetupPost)

        self.form = [self.formFence]


    def addPath(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.path = sel[0]
            self.linePath.setText(self.path.Label)
            self.fence.Path = self.path

        FreeCAD.ActiveDocument.recompute()



if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantProyectToMesh', _CommandToolProyectToMesh())