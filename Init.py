# -*- coding: utf-8 -*-
#****************************************************************************
#*                                                                          *
#*  Kicad STEPUP (TM) (3D kicad board and models to STEP) for FreeCAD       *
#*  3D exporter for FreeCAD                                                 *
#*  Kicad STEPUP TOOLS (TM) (3D kicad board and models to STEP) for FreeCAD *
#*  Copyright (c) 2015                                                      *
#*  Maurice easyw@katamail.com                                              *
#*                                                                          *
#*  Kicad STEPUP (TM) is a TradeMark and cannot be freely useable           *
#*                                                                          *

#FreeCAD.addImportType("Kicad pcb board/mod File Type (*.kicad_pcb *.kicad_mod)","kicadStepUptools") 


FreeCAD.addImportType("Industry Foundation Classes (*.ifc)","importIFC")
FreeCAD.addExportType("Industry Foundation Classes (*.ifc)","importIFC")
FreeCAD.addImportType("Wavefront OBJ - Arch module (*.obj)","importOBJ")
FreeCAD.addExportType("Wavefront OBJ - Arch module (*.obj)","importOBJ")
FreeCAD.addExportType("WebGL file (*.html)","importWebGL")
FreeCAD.addExportType("JavaScript Object Notation (*.json)","importJSON")
FreeCAD.addImportType("Collada (*.dae)","importDAE")
FreeCAD.addExportType("Collada (*.dae)","importDAE")
FreeCAD.addImportType("3D Studio mesh (*.3ds)","import3DS")
FreeCAD.addImportType("SweetHome3D XML export (*.zip)","importSH3D")