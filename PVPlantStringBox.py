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

if FreeCAD.GuiUp:
    import FreeCADGui, os
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
    from pivy import coin
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

import PVPlantResources

def makeStringbox():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "StringBox")
    _StringBox(obj)
    _ViewProviderStringBox(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    #FreeCADGui.ActiveDocument.ActiveView.fitAll()
    return obj

class _StringBox(ArchComponent.Component):

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setProperties(obj)
        self.Type = "StringBox"

        # Does a IfcType exist?
        obj.IfcType = "Electric Distribution Board"
        obj.setEditorMode("IfcType", 1)
        # obj.MoveWithHost = False

    def setProperties(self, obj):
        # Definicion de Propiedades:
        '''[
        'App::PropertyBool',
        'App::PropertyBoolList',
        'App::PropertyFloat',
        'App::PropertyFloatList',
        'App::PropertyFloatConstraint',
        'App::PropertyPrecision',
        'App::PropertyQuantity',
        'App::PropertyQuantityConstraint',
        'App::PropertyAngle',
        'App::PropertyDistance',
        'App::PropertyLength',
        'App::PropertyArea',
        'App::PropertyVolume',
        'App::PropertyFrequency',
        'App::PropertySpeed',
        'App::PropertyAcceleration',
        'App::PropertyForce',
        'App::PropertyPressure',
        'App::PropertyVacuumPermittivity',
        'App::PropertyInteger',
        'App::PropertyIntegerConstraint',
        'App::PropertyPercent',
        'App::PropertyEnumeration',
        'App::PropertyIntegerList',
        'App::PropertyIntegerSet',
        'App::PropertyMap',
        'App::PropertyString',
        'App::PropertyPersistentObject',
        'App::PropertyUUID',
        'App::PropertyFont',
        'App::PropertyStringList',
        'App::PropertyLink',
        'App::PropertyLinkChild',
        'App::PropertyLinkGlobal',
        'App::PropertyLinkHidden',
        'App::PropertyLinkSub',
        'App::PropertyLinkSubChild',
        'App::PropertyLinkSubGlobal',
        'App::PropertyLinkSubHidden',
        'App::PropertyLinkList',
        'App::PropertyLinkListChild',
        'App::PropertyLinkListGlobal',
        'App::PropertyLinkListHidden',
        'App::PropertyLinkSubList',
        'App::PropertyLinkSubListChild',
        'App::PropertyLinkSubListGlobal',
        'App::PropertyLinkSubListHidden',
        'App::PropertyXLink',
        'App::PropertyXLinkSub',
        'App::PropertyXLinkSubList',
        'App::PropertyXLinkList',
        'App::PropertyMatrix',
        'App::PropertyVector',
        'App::PropertyVectorDistance',
        'App::PropertyPosition',
        'App::PropertyDirection',
        'App::PropertyVectorList',
        'App::PropertyPlacement',
        'App::PropertyPlacementList',
        'App::PropertyPlacementLink',
        'App::PropertyColor',
        'App::PropertyColorList',
        'App::PropertyMaterial',
        'App::PropertyMaterialList',
        'App::PropertyPath',
        'App::PropertyFile',
        'App::PropertyFileIncluded',
        'App::PropertyPythonObject',
        'App::PropertyExpressionEngine',
        'Part::PropertyPartShape',
        'Part::PropertyGeometryList',
        'Part::PropertyShapeHistory',
        'Part::PropertyFilletEdges',
        'Mesh::PropertyNormalList',
        'Mesh::PropertyCurvatureList',
        'Mesh::PropertyMeshKernel',
        'Sketcher::PropertyConstraintList'
        ]'''

        pl = obj.PropertiesList
        if not "InputsFromStrings" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "InputsFromStrings",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "Connection ")).InputsFromStrings = 12

        if not ("PositiveInputs" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "PositiveInputs",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).PositiveInputs = []
            obj.setEditorMode("PositiveInputs", 1)

        if not ("NegativeInputs" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "NegativeInputs",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).NegativeInputs = []
            obj.setEditorMode("NegativeInputs", 1)

        if not "InputCables" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "InputCables",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "InputCables"))

        # Outputs
        '''
        if not "Outputs" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "Outputs",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "Connection ")).Outputs = 1
        '''

        if not ("PositiveOut" in pl):
            obj.addProperty("Part::PropertyPartShape",
                            "PositiveOut",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )
            obj.setEditorMode("PositiveOut", 1)

        if not ("NegativeOut" in pl):
            obj.addProperty("Part::PropertyPartShape",
                            "NegativeOut",
                            "Connections",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )
            obj.setEditorMode("NegativeOut", 1)

        # Size:
        if not "Width" in pl:
            obj.addProperty("App::PropertyLength",
                            "Width",
                            "Box",
                            QT_TRANSLATE_NOOP("App::Property", "Connection ")).Width = 330

        if not "Length" in pl:
            obj.addProperty("App::PropertyLength",
                            "Length",
                            "Box",
                            QT_TRANSLATE_NOOP("App::Property", "Connection ")).Length = 848

        if not "Height" in pl:
            obj.addProperty("App::PropertyLength",
                            "Height",
                            "Box",
                            QT_TRANSLATE_NOOP("App::Property", "Connection ")).Height = 615


    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and Arch wall properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)
        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

        if prop == "InputsFromStrings":
            for i in range(int(obj.getPropertyByName(prop).Value)):
                obj.removeProperty("PositiveInput" + str(i+1))
                obj.removeProperty("NegativeInput" + str(i + 1))


    def execute(self, obj):
        solids = []
        pts = []

        def getdownFace(object):
            downface = object.Faces[0]
            for face in object.Faces:
                if face.CenterOfMass.z < downface.CenterOfMass.z:
                    downface = face
            return downface

        def drawInputs(numrows, offsetx, type, cpd):
            numInputs = int(obj.InputsFromStrings.Value)
            nperrow = int(round(numInputs / numrows, 0))
            gap = 45
            diameter = 20
            points = []
            cnt = 0
            for r in range(numrows):
                xx = -obj.Length.Value / 2 + offsetx + gap / 2 * (r % 2)
                yy = -diameter + gap * r
                for i in range(min(numInputs, nperrow)):
                    cyl = Part.makeCylinder(10, 20, FreeCAD.Vector(xx + gap * i, yy, -20))
                    solids.append(cyl)
                    points.append(getdownFace(cyl).CenterOfMass)
                    cnt += 1
                    inname = ("PositiveIn" if type == 0 else "NegativeIn") + str(cnt)
                    obj.addProperty("Part::PropertyPartShape",
                                    inname,
                                    "Inputs",
                                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                                    )
                    obj.setEditorMode(inname, 1)
                    setattr(obj, inname, getdownFace(cyl))
                    cpd.add(cyl)
                numInputs -= nperrow
            return points

        box = Part.makeBox(obj.Length.Value, obj.Width.Value, obj.Height.Value)
        box.Placement.Base.x -= obj.Length.Value / 2
        box.Placement.Base.y -= obj.Width.Value / 2

        # Output:
        cpd_out = Part.makeCompound([])
        outp = Part.makeCylinder(65/2, 20, FreeCAD.Vector(0, 0, -20))
        #out.Placement.Base.x += 50
        #out.Placement.Base.y += 65/2
        solids.append(outp)
        cpd_out.add(outp)
        obj.PositiveOut = getdownFace(outp)

        outn = outp.copy()
        outn.Placement.Base.x += 65 + 10
        solids.append(outn)
        cpd_out.add(outn)
        obj.NegativeOut = getdownFace(outn)

        # Inputs:
        cpd_Pos_Inputs = Part.makeCompound([])
        cpd_Neg_Inputs = Part.makeCompound([])
        obj.PositiveInputs = drawInputs(2,  80, 0, cpd_Pos_Inputs).copy()
        obj.NegativeInputs = drawInputs(4, 650, 1, cpd_Neg_Inputs).copy()

        pts.append(getdownFace(box).CenterOfMass)
        pts.append(getdownFace(outn).CenterOfMass)
        pts.append(getdownFace(outp).CenterOfMass)

        obj.Shape = Part.makeCompound([box, cpd_out, cpd_Pos_Inputs, cpd_Neg_Inputs])

class _ViewProviderStringBox(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "StringBox.svg"))

    def attach(self, vobj):
        self.Object = vobj.Object
        sep = coin.SoSeparator()
        self.coords = coin.SoCoordinate3()
        sep.addChild(self.coords)
        self.coords.point.deleteValues(0)
        symbol = coin.SoMarkerSet()
        symbol.markerIndex = FreeCADGui.getMarkerIndex("", 5)
        sep.addChild(symbol)
        rn = vobj.RootNode
        rn.addChild(sep)
        ArchComponent.ViewProviderComponent.attach(self, vobj)

    def updateData(self, obj, prop):

        if prop == "PositiveInputs":
            if obj.PositiveInputs:
                self.coords.point.setNum(len(obj.PositiveInputs))
                self.coords.point.setValues([[p.x, p.y, p.z] for p in obj.PositiveInputs])
            else:
                self.coords.point.deleteValues(0)


class _CommandBoxEnclosure:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "StringBox.svg")),
                'Accel': "C, E",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Movimiento de tierras"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Calcular el movimiento de tierras")}

    def Activated(self):
        makeStringbox()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantStringBox', _CommandBoxEnclosure())