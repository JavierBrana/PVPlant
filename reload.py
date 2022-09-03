import FreeCAD
if FreeCAD.GuiUp:
    import FreeCADGui, os
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt,txt):
        return txt
    def QT_TRANSLATE_NOOP(ctxt,txt):
        return txt
    # \endcond

global __dir__
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")


class _CommandReload:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(__dir__, "Resources", "Icons", "Reload.svg")),
                'Accel': "R,E",
                'MenuText': QT_TRANSLATE_NOOP("Reload","Reload"),
                'ToolTip': QT_TRANSLATE_NOOP("Reload","Reload")}

    def Activated(self):
        import PVPlantPlacement, \
            PVPlantGeoreferencing, PVPlantImportGrid, PVPlantTerrainAnalisys, \
            PVPlantSite, PVPlantRack, PVPlantFence, PVPlantFencePost, PVPlantCreateTerrainMesh, \
            PVPlantFoundation, PVPlantTreeGenerator, PVPlantBuilding, exportPVSyst, \
            PVPlantTrench, PVPlantEarthWorks, PVPlantStringBox, PVPlantCable, PVPlantPad, \
            PVPlantRoad, PVPlantTerrain, PVPlantStringing, PVPlantManhole, \
            PVPlantBOQMechanical, PVPlantBOQElectrical, PVPlantArea, GraphProfile
        from Utils import PVPlantUtils
        from Utils import PVPlantTrace, gui_edit, profile_editor, graphics
        #from  Lib import GoogleMapDownloader

        import importlib
        importlib.reload(PVPlantPlacement)
        importlib.reload(PVPlantImportGrid)
        importlib.reload(PVPlantGeoreferencing)
        importlib.reload(PVPlantTerrainAnalisys)
        importlib.reload(PVPlantSite)
        importlib.reload(PVPlantRack)
        importlib.reload(PVPlantFence)
        importlib.reload(PVPlantFencePost)
        importlib.reload(PVPlantFoundation)
        importlib.reload(PVPlantCreateTerrainMesh)
        importlib.reload(PVPlantTreeGenerator)
        importlib.reload(PVPlantBuilding)
        importlib.reload(exportPVSyst)
        importlib.reload(PVPlantTrench)
        importlib.reload(PVPlantEarthWorks)
        importlib.reload(PVPlantStringBox)
        importlib.reload(PVPlantCable)
        importlib.reload(PVPlantPad)
        importlib.reload(PVPlantRoad)
        importlib.reload(PVPlantTerrain)
        importlib.reload(PVPlantStringing)
        importlib.reload(PVPlantBOQMechanical)
        importlib.reload(PVPlantBOQElectrical)
        importlib.reload(PVPlantArea)
        importlib.reload(PVPlantUtils)
        importlib.reload(PVPlantManhole)
        importlib.reload(GraphProfile)

        importlib.reload(PVPlantTrace)
        importlib.reload(gui_edit)
        importlib.reload(profile_editor)
        importlib.reload(graphics)

        #importlib.reload(GoogleMapDownloader)
        print("Reload modules...")


    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Reload', _CommandReload())