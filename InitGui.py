

__title__="FreeCAD Fotovoltaic Power Plant Toolkit"
__author__ = "Javier Braña"
__url__ = "sn"


class PVPlantWorkbench (Workbench):
    import os
    from PVPlantResources import DirIcons as DirIcons

    MenuText = "PVPlant Workbench"
    ToolTip = "A description of my workbench"
    Icon = str(os.path.join(DirIcons, "solar-panel.svg"))

    def Initialize(self):

        # Mias
        import PVPlantGeoreferencing,  PVPlantRack, PVPlantPlacement, \
            PVPlant_Import, PVPlantTerrainAnalisys, PVPlantSite, PVPlantImportGrid,PVPlantFence,\
            PVPlantFoundation, PVPlantCreateTerrainMesh, \
            PVPlantTreeGenerator, exportPVSyst, PVPlantTrench, PVPEarthWorks, PVPlantBOQFrames, \
            PVPlantStringBox, PVPlantCable, PVPlantPad, PVPlantRoad, \
            reload

        # A list of command names created in the line above
        self.list = ["Reload",
                     "PVPlantSite",
                     "PVPlantGeoreferencing",
                     #"ImportGrid",
                     "PointsGroup",
                     "PVPlantCreateTerrainMesh",
                     "TerrainAnalisys",
                     "PVPlantTrench",
                     "PVPlantEarthworks",
                     "PVPlantPad",
                     "PVPlantRoad",
                     ]
        self.list1 = [
                     "RackType",
                     "PVPlantPlacement",
                     "PVPlantAdjustToTerrain",
                     "PVPlantConvertTo",
                     ]

        self.list2 = [
                    "PVPlantTree",
                    "PVPlantFenceGroup",
                    ]

        self.list3 = ["ExportToPVSyst",
                      "PVPlantBOQMechanical",
                    ]

        self.electricalList = ["PVPlantStringBox",
                               "PVPlantCable",
                              ]

        self.roads = ["PVPlantRoad",

                     ]

        self.pads =  ["PVPlantPad",
                      "Separator"

                     ]

        # Toolbar
        self.appendToolbar("Civil", self.list)  # creates a new toolbar with your commands
        self.appendToolbar("PVPlant", self.list1)  # creates a new toolbar with your commands
        self.appendToolbar("Shadow", self.list2)  # creates a new toolbar with your commands
        self.appendToolbar("Outputs", self.list3)  # creates a new toolbar with your commands
        self.appendToolbar("Electrical", self.electricalList)  # creates a new toolbar with your commands

        # Menu
        self.appendMenu("&Civil", self.list)  # creates a new menu
        self.appendMenu("&PVPlant", self.list1)  # creates a new menu
        self.appendMenu("&Shadow", self.list2)  # creates a new menu
        self.appendMenu("&Outputs", self.list3)  # creates a new menu
        self.appendMenu("&Electrical", self.electricalList)  # creates a new menu

        # Draft tools
        import DraftTools, DraftGui, Draft_rc
        from DraftTools import translate
        self.drafttools = ["Draft_Line","Draft_Wire","Draft_Circle","Draft_Arc","Draft_Ellipse",
                        "Draft_Polygon","Draft_Rectangle", "Draft_Text",
                        "Draft_Dimension", "Draft_BSpline","Draft_Point",
                        "Draft_Facebinder","Draft_BezCurve","Draft_Label"]
        self.draftmodtools = ["Draft_Move","Draft_Rotate","Draft_Offset",
                        "Draft_Trimex", "Draft_Upgrade", "Draft_Downgrade", "Draft_Scale",
                        "Draft_Shape2DView","Draft_Draft2Sketch","Draft_Array",
                        "Draft_Clone"]
        self.draftextratools = ["Draft_WireToBSpline","Draft_ShapeString",
                                "Draft_PathArray","Draft_Mirror","Draft_Stretch"]
        self.draftcontexttools = ["Draft_ApplyStyle","Draft_ToggleDisplayMode","Draft_AddToGroup","Draft_AutoGroup",
                            "Draft_SelectGroup","Draft_SelectPlane",
                            "Draft_ShowSnapBar","Draft_ToggleGrid","Draft_UndoLine",
                            "Draft_FinishLine","Draft_CloseLine"]
        self.draftutils = ["Draft_Heal","Draft_FlipDimension",
                           "Draft_ToggleConstructionMode","Draft_ToggleContinueMode","Draft_Edit",
                           "Draft_Slope","Draft_AddConstruction"]
        self.snapList = ['Draft_Snap_Lock','Draft_Snap_Midpoint','Draft_Snap_Perpendicular',
                         'Draft_Snap_Grid','Draft_Snap_Intersection','Draft_Snap_Parallel',
                         'Draft_Snap_Endpoint','Draft_Snap_Angle','Draft_Snap_Center',
                         'Draft_Snap_Extension','Draft_Snap_Near','Draft_Snap_Ortho','Draft_Snap_Special',
                         'Draft_Snap_Dimensions','Draft_Snap_WorkingPlane']

        def QT_TRANSLATE_NOOP(scope, text): return text
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Draft tools"), self.drafttools)
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Draft mod tools"), self.draftmodtools)
        self.appendMenu(QT_TRANSLATE_NOOP("arch", "&Draft"), self.drafttools + self.draftmodtools + self.draftextratools)
        self.appendMenu([QT_TRANSLATE_NOOP("arch", "&Draft"), QT_TRANSLATE_NOOP("arch", "Utilities")], self.draftutils + self.draftcontexttools)
        self.appendMenu([QT_TRANSLATE_NOOP("arch", "&Draft"), QT_TRANSLATE_NOOP("arch", "Snapping")], self.snapList)

    def Activated(self):
        "This function is executed when the workbench is activated"
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        # "recipient" will be either "view" or "tree"

        #if FreeCAD.activeDraftCommand is None:
        if recipient.lower() == "view":
            print("Menus en la 'View'")
            #if FreeCAD.activeDraftCommand is None:
            presel = FreeCADGui.Selection.getPreselection()
            print(presel.SubElementNames, " - ", presel.PickedPoints)
            if not presel is None:
                if presel.Object.Proxy.Type == "Road":
                    self.appendContextMenu("Road", self.roads)
                elif presel.Object.Proxy.Type == "Pad":
                    self.appendContextMenu("Pad", self.pads)

        '''
        self.contextMenu = QtGui.QMenu()
        menu_item_remove_selected = self.contextMenu.addAction("Remove selected geometry")
        menu_item_remove_all = self.contextMenu.addAction("Clear list")
        if not self.references:
            menu_item_remove_selected.setDisabled(True)
            menu_item_remove_all.setDisabled(True)
        self.connect(
            menu_item_remove_selected,
            QtCore.SIGNAL("triggered()"),
            self.remove_selected_reference
        )
        self.connect(
            menu_item_remove_all,
            QtCore.SIGNAL("triggered()"),
            self.remove_all_references
        )
        parentPosition = self.list_References.mapToGlobal(QtCore.QPoint(0, 0))
        self.contextMenu.move(parentPosition + QPos)
        self.contextMenu.show()
        '''

    def GetClassName(self): 
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"

Gui.addWorkbench(PVPlantWorkbench())
