import FreeCAD

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import os
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond


global __dir__
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
icon = os.path.join(__dir__, "Resources", "Icons", "Location.svg")

class _CommandPVPlantGeoreferencing:

    def GetResources(self):
        return {'Pixmap': str(icon),
                'Accel': "G, R",
                'MenuText': QT_TRANSLATE_NOOP("Georeferencing","Georeferencing"),
                'ToolTip': QT_TRANSLATE_NOOP("Georeferencing","Referenciar el lugar")}

    def Activated(self):
        import PVPlantForms

        self.form = PVPlantForms.MapWindow()
        QtCore.QObject.connect(self.form.bAccept, QtCore.SIGNAL("clicked()"), self.runbl)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def runbl(self):
        s = 15
        lat = self.form.lat
        lon = self.form.lon
        self.form.close()
        import utm
        RefUTM = utm.from_latlon(lat, lon)
        print (RefUTM)

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantGeoreferencing',_CommandPVPlantGeoreferencing())