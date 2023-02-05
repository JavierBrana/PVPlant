
import FreeCAD
import ArchComponent
import PVPlantSite
import copy
import Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "PVPlant Export to DXF"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons
from PVPlantResources import DirDocuments as DirDocuments
import ezdxf


def importDXF(filename):
    print("---------- import to dxf ----------")

    if filename == "":
        return

    import sys
    import ezdxf

    doc = None
    try:
        doc = ezdxf.readfile(filename)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        sys.exit(2)

    # iteration
    for layer in doc.layers:
        print(layer.dxf.name)

        #if layer.dxf.name != "0":
        #    layer.off()  # switch all layers off except layer "0"

    # check for existing layer definition
    if "MyLines" in doc.layers:
        layer = doc.layers.get("MyLines")

    layer_count = len(doc.layers)  # total count of layer definitions


class _PVPlantImportDXF:
    '''The editmode TaskPanel to select what you want to export'''

    def __init__(self):
        self.doc = None

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "importDXF.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "dxf.svg")))
        self.form.buttonOpen.clicked.connect(self.openFile)
        self.form.listLayer.currentItemChanged.connect(self.onLayerSelect)

    def openFile(self):
        ''' '''
        "getOpenFileName(parent: typing.Union[PySide2.QtWidgets.QWidget, NoneType] = None," \
        "caption: str = ''," \
        "dir: str = ''," \
        "filter: str = ''," \
        "options: PySide2.QtWidgets.QFileDialog.Options = Default(QFileDialog.Options)) -> typing.Tuple[str, str]"
        filename, trash = QtGui.QFileDialog().getOpenFileName(None, 'Select File', os.getcwd(), 'Autocad dxf (*.dxf)')
        if filename == "":
            return

        import sys
        import ezdxf

        try:
            self.doc = ezdxf.readfile(filename)
        except IOError:
            print(f"Not a DXF file or a generic I/O error.")
            sys.exit(1)
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file.")
            sys.exit(2)

        # iteration
        self.form.listLayer.clear()
        for layer in self.doc.layers:
            self.form.listLayer.addItem(layer.dxf.name)

        msp = self.doc.modelspace()
        for e in msp:
            print(e.dxftype())
            #self.form.listObjects.addItem(e.dxftype())

    def onLayerSelect(self, item):
        ''' '''
        print(item.text())
        self.form.listLayer.clear()
        if self.doc:
            msp = self.doc.modelspace()
            '''
            layer = self.doc.layers.get(item.text())
            for obj in layer.entities_in_redraw_order(reverse=False):
                self.form.listObjects.addItem(obj)
            '''
            for obj in msp.query('*[layer=="'+item.text()+'"]'):
                #self.form.listObjects.addItem(obj)
                print(obj)

    def accept(self):
        ''' '''

class CommandImportDXF:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "dxf.svg")),
                'Accel': "E, X",
                'MenuText': "Import to DXF",
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Import choosed layers to dxf")}

    def Activated(self):
        taskd = _PVPlantImportDXF()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('importDXF', CommandImportDXF())