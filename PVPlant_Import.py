import FreeCAD

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond


import os
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")


class CommandImportGrid:
    "the Arch Panel Cut command definition"
    def GetResources(self):
        return {'Pixmap'  : str(os.path.join(DirIcons, "Elevation.svg")),
                'MenuText': QT_TRANSLATE_NOOP("Arch_Panel_Cut","Grid"),
                'Accel': "I, K",
                'ToolTip': QT_TRANSLATE_NOOP("Arch_Panel_Sheet","Grid form Google Maps")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        import PVPlantForms
        print("algo")
        self.form = PVPlantForms.MapWindow()
        #QtCore.QObject.connect(self.form.bAccept, QtCore.SIGNAL("clicked()"), self.runbl)

    def runbl(self):
        lat = self.form.lat
        lon = self.form.lon
        self.form.close()
        import PVPlantImportGrid
        PVPlantImportGrid.import_heights(float(lat), float(lon), float(15))


if FreeCAD.GuiUp:
    class CommandPanelGroup:

        def GetCommands(self):
            return tuple(['ImportKMZ','ImportGrid'])
        def GetResources(self):
            return {
                    'ToolTip': QT_TRANSLATE_NOOP("Arch_PanelTools", 'Panel tools'),
                    'MenuText': QT_TRANSLATE_NOOP("Arch_PanelTools",'Panel tools')
                   }
        def IsActive(self):
            return not FreeCAD.ActiveDocument is None


    FreeCADGui.addCommand('ImportGrid', CommandImportGrid())