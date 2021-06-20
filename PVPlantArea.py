
import FreeCAD,Draft,ArchCommands,ArchFloor,math,re,datetime
import ArchSite
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond

import os
from PVPlantResources import DirIcons as DirIcons

__title__="FreeCAD Site"
__author__ = ""
__url__ = "http://www.freecadweb.org"












## Comando: -----------------------------------------------------------------------------------------------------------
class _CommandBoundary:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "A, B",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        taskd = _PVPlantPlacementTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class _CommandPVArea:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "A, P",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        taskd = _PVPlantPlacementTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class _CommandPVArea:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "A, P",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        taskd = _PVPlantPlacementTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantPlacement', _CommandBoundary())
    FreeCADGui.addCommand('PVPlantPlacement', _CommandPVArea())