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
import ArchComponent
import Part
import PVPlantSite
import copy
import numpy as np

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from pivy import coin
    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt

    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "FreeCAD Fixed Rack"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons

class SelObserver:
    def __init__(self):
        self.ui = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/SelectionObserver.ui")
        self.clearUI()

    def addSelection(self, document, object, element, position):  # Selection
        '''  '''
        import PVPlantRack
        sel = FreeCADGui.Selection.getSelection()
        if sel:
            if hasattr(sel[0], "Proxy"):
                if issubclass(sel[0].Proxy.__class__, PVPlantRack.Frame):
                    self.ui.setParent(FreeCADGui.getMainWindow())
                    self.ui.setWindowFlags(QtCore.Qt.Window)
                    self.setUI(sel[0])
                    #self.ui.move(QtGui.QCursor.pos())
                    self.ui.show()

    def clearSelection(self, doc):
        ''' '''
        self.ui.hide()
        self.clearUI()

    def clearUI(self):
        self.ui.editName.setText("")
        self.ui.editPosX.setValue(0)
        self.ui.editPosY.setValue(0)
        self.ui.editPosZ.setValue(0)
        self.ui.editAngleX.setValue(0)
        self.ui.editAngleY.setValue(0)
        self.ui.editPercentX.setValue(0)
        self.ui.editPercentY.setValue(0)

    def setUI(self, obj):
        import math
        pos = obj.Placement.Base
        angles = obj.Placement.Rotation.toEulerAngles("XYZ")

        self.ui.editName.setText(obj.Label)
        self.ui.editPosX.setValue(pos.x)
        self.ui.editPosY.setValue(pos.y)
        self.ui.editPosZ.setValue(pos.z)
        self.ui.editAngleX.setValue(angles[0])
        self.ui.editAngleY.setValue(angles[1])
        self.ui.editPercentX.setValue( math.tan(math.radians(angles[0])) * 100)
        self.ui.editPercentY.setValue( math.tan(math.radians(angles[1])) * 100)
