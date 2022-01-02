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
import PVPlantSite
import copy

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import PySide.QtGui as QtGui
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

import os
from PVPlantResources import DirIcons as DirIcons

def makePVPlantFenceGate():
    obj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'FenceGate')
    _FenceGate(obj)
    _ViewProviderFenceGate(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj

class _FenceGate(ArchComponent.Component):
    def __init__(self, obj):
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)

        # Does a IfcType exist?
        # obj.IfcType = "Fence"

    def setProperties(self, obj):
        ArchComponent.Component.setProperties(self, obj)

        pl = obj.PropertiesList

        if not "Post" in pl:
            obj.addProperty("App::PropertyLink",
                            "Post",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post"))

        if not "Foundation" in pl:
            obj.addProperty("App::PropertyLength",
                            "Foundation",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post"))

        if not "Depth" in pl:
            obj.addProperty("App::PropertyLength",
                            "Depth",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post")).Depth = 650

        if not "Gap" in pl:
            obj.addProperty("App::PropertyLength",
                            "Gap",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post")).Gap = 4000

        if not "Angle" in pl:
            obj.addProperty("App::PropertyAngle",
                            "Angle",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post")).Angle = 60

        if not "MeshOffsetZ" in pl:
            obj.addProperty("App::PropertyLength",
                            "MeshOffsetZ",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post")).MeshOffsetZ = 0

        if not "MeshHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "MeshHeight",
                            "Fence",
                            QT_TRANSLATE_NOOP("App::Property", "A single fence post")).MeshHeight = 2000

        ########## Datos informativos:
        if not "NumberOfSections" in pl:
            obj.addProperty("App::PropertyInteger",
                            "NumberOfSections",
                            "Output",
                            QT_TRANSLATE_NOOP("App::Property", "The number of sections the fence is built of"))
            obj.setEditorMode("NumberOfSections", 1)

        if not "NumberOfPosts" in pl:
            obj.addProperty("App::PropertyQuantity",
                            "NumberOfPosts",
                            "Output",
                            QT_TRANSLATE_NOOP("App::Property", "The number of posts used to build the fence"))
            obj.setEditorMode("NumberOfPosts", 1)

        if not "Length" in pl:
            obj.addProperty("App::PropertyLength",
                            "Length",
                            "Output",
                            QT_TRANSLATE_NOOP("App::Property", "The number of posts used to build the fence"))
            obj.setEditorMode("Length", 1)

        if not "PlacementList" in pl:
            obj.addProperty("App::PropertyPlacementList",
                            "PlacementList",
                            "Output",
                            QT_TRANSLATE_NOOP("App::Property", "The number of posts used to build the fence"))
            obj.setEditorMode("Length", 1)

        self.Type = "PVPlatFence"

    def __getstate__(self):
        if hasattr(self, 'sectionFaceNumbers'):
            return (self.sectionFaceNumbers)
        return None

    def __setstate__(self, state):
        if state is not None and isinstance(state, tuple):
            self.sectionFaceNumbers = state[0]
        return None

    def execute(self, obj):
        import Part

        pathwire = self.calculatePathWire(obj)
        if not pathwire:
            # FreeCAD.Console.PrintLog("ArchFence.execute: path " + obj.Base.Name + " has no edges\n")
            return
        '''
        if not obj.Section:
            FreeCAD.Console.PrintLog("ArchFence.execute: Section not set\n")
            return
        '''
        if not obj.Post:
            FreeCAD.Console.PrintLog("ArchFence.execute: Post not set\n")
            return

        self.Posts = []
        self.Foundations = []
        site = PVPlantSite.get()
        land = site.Terrain.Shape

        land_coppy = land.copy()
        land_coppy.Placement.Base -= site.Origin
        pathwire = pathwire.copy()
        pathwire.Placement.Base -= site.Origin
        proj = land_coppy.makeParallelProjection(pathwire, FreeCAD.Vector(0, 0, 1))
        pathwire = Part.Wire(proj.Edges)

        pathLength = pathwire.Length
        sectionLength = obj.Gap.Value
        postLength = obj.Post.Shape.BoundBox.XMax
        allShapes = []
        postPlacements = []
        pathsegments = self.calculateSegments(obj, pathwire)

        count = 0
        drawFirstPost = True
        pathLength = 0
        for seg in pathsegments:
            segwire = Part.Wire(seg)
            segLength = segwire.Length
            pathLength += segLength

            obj.NumberOfSections = self.calculateNumberOfSections(segLength, sectionLength, postLength)
            obj.NumberOfPosts = obj.NumberOfSections + 1

            count += obj.NumberOfSections

            downRotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
            placements = self.calculatePostPlacements(obj, segwire, downRotation)

            if drawFirstPost:
                drawFirstPost = False
            else:
                placements.pop(0)

            postPlacements.extend(placements)

        obj.NumberOfSections = count
        obj.NumberOfPosts = obj.NumberOfSections + 1
        obj.Length = pathLength

        postShapes, postFoundation = self.calculatePosts(obj, postPlacements)
        sections, num = self.calculateSections(obj, postPlacements)

        allShapes.extend(postShapes)
        allShapes.extend(postFoundation)
        allShapes.extend(sections)

        compound = Part.makeCompound(allShapes)
        obj.Shape = compound
        obj.Placement.Base += site.Origin

    def calculateSegments(self, obj, pathwire):
        import math
        segments = []
        segment = [pathwire.Edges[0]]
        segments.append(segment)
        for ind in range(len(pathwire.Edges) - 1):
            ed1 = pathwire.Edges[ind]
            ed2 = pathwire.Edges[ind + 1]
            vec1 = ed1.Vertexes[1].Point - ed1.Vertexes[0].Point
            vec2 = ed2.Vertexes[1].Point - ed2.Vertexes[0].Point

            angle = math.degrees(vec1.getAngle(vec2))
            if angle > obj.Angle.Value:
                segment = []
                segments.append(segment)
            segment.append(ed2)

        return segments

    def calculateNumberOfSections(self, pathLength, sectionLength, postLength):
        withoutLastPost = pathLength - postLength
        realSectionLength = sectionLength + postLength
        return math.ceil(withoutLastPost / realSectionLength)

    def calculatePostPlacements(self, obj, pathwire, rotation):
        postWidth = obj.Post.Diameter.Value
        transformationVector = FreeCAD.Vector(0, postWidth, 0)
        #transformationVector = FreeCAD.Vector(0, 0, 0)
        if False:
            placements = []
            for e in pathwire.Edges:
                num = math.ceil(e.Length / obj.Section.Shape.BoundBox.XMax)
                pl = calculatePlacementsOnPath(rotation, e, num, transformationVector, True)
                pl.append(pl.pop(1))
                print(pl)
                placements.extend(pl)
                print(placements)
                print("-----------------------------------------------------\n")
        else:
            placements = calculatePlacementsOnPath(rotation, pathwire, obj.NumberOfSections + 1, transformationVector, True)
            # The placement of the last object is always the second entry in the list.
            # So we move it to the end
            placements.append(placements.pop(1))

        return placements

    def calculatePosts(self, obj, postPlacements):
        import Draft, Part

        posts = []
        foundations = []
        for placement in postPlacements:
            postCopy = obj.Post.Shape.copy()
            postCopy = Part.Solid(postCopy)
            postCopy.Placement = placement
            postCopy.Placement.Base.z += 100
            posts.append(postCopy)

            foundation = Part.makeCylinder(150, 700)
            foundation.Placement = placement
            foundation.Placement.Base.z -= obj.Depth.Value
            foundation = foundation.cut(postCopy)
            foundations.append(foundation)

        return posts, foundations

    def calculateSections(self, obj, postPlacements):
        import Part

        shapes = []
        faceNumbers = []

        offsetz = obj.MeshOffsetZ.Value
        meshHeight = obj.MeshHeight.Value
        for i in range(len(postPlacements) - 1):
            startPlacement = postPlacements[i]
            endPlacement = postPlacements[i + 1]

            p1 = startPlacement.Base + FreeCAD.Vector(0, 0, offsetz)
            p2 = endPlacement.Base + FreeCAD.Vector(0, 0, offsetz)
            p3 = p2 + FreeCAD.Vector(0, 0, meshHeight)
            p4 = p1 + FreeCAD.Vector(0, 0, meshHeight)
            pointlist = [p1, p2, p3, p4, p1]

            try:
                pol = Part.makePolygon(pointlist)
                face = Part.Face(pol)
                shapes.append(face)
                faceNumbers.append(1)
            except:
                print("No es posible crear la cara: ---------------------------------------------------")
                print("  +++++ Start: ", startPlacement.Base, " - end: ", endPlacement.Base)
                print("  +++++ algo: ", pointlist, "\n")
                print("---------------------------------------------------\n")
        return (shapes, faceNumbers)

    def calculatePathWire(self, obj):
        if obj.Base:
            wire = None
            if hasattr(obj.Base.Shape, 'Wires') and obj.Base.Shape.Wires:
                wire = obj.Base.Shape.Wires[0]
            elif obj.Base.Shape.Edges:
                wire = Part.Wire(obj.Base.Shape.Edges)
            return wire
        return None


class _ViewProviderFenceGate(ArchComponent.ViewProviderComponent):
    "A View Provider for the Fence object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "fence.svg"))

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''

        # GeoCoords Node.
        self.geo_coords = coin.SoGeoCoordinate()

        # Surface features.
        self.triangles = coin.SoIndexedFaceSet()
        self.face_material = coin.SoMaterial()
        self.edge_material = coin.SoMaterial()
        self.edge_color = coin.SoBaseColor()
        self.edge_style = coin.SoDrawStyle()
        self.edge_style.style = coin.SoDrawStyle.LINES

        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.PER_FACE
        offset = coin.SoPolygonOffset()

        # Face root.
        faces = coin.SoSeparator()
        faces.addChild(shape_hints)
        faces.addChild(self.face_material)
        faces.addChild(mat_binding)
        faces.addChild(self.geo_coords)
        faces.addChild(self.triangles)

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        faces.addChild(shape_hints)
        highlight.addChild(self.edge_material)
        highlight.addChild(mat_binding)
        highlight.addChild(self.edge_style)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        origin = PVPlantSite.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0
        print("  - Propiedad: ", prop)

        if prop == "Shape":
            shape = obj.getPropertyByName(prop)

            # Get GeoOrigin.
            points = [ver.Point for ver in shape.Vertexes]

            # Set GeoCoords.
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            self.geo_coords.geoSystem.setValues(geo_system)
            self.geo_coords.point.values = points


    def claimChildren(self):
        children = []

        if self.Object.Post:
            children.append(self.Object.Post)

        if self.Object.Base:
            children.append(self.Object.Base)

        return children

class _FenceGateTaskPanel:
    '''The TaskPanel to setup the fence'''

    def __init__(self):
        self.section = None
        self.post = None
        self.path = None

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

        self.buttonPathSelect.clicked.connect(self.addPath)
        self.valueInterval.valueChanged.connect(self.SetupGrid)
        self.valueHeight.valueChanged.connect(self.SetupGrid)
        # self.valueDepth.valueChanged.connect(self.SetupPost)

        # Form para configurar el poste: -------------------------------------------------------------------
        self.formPost = QtGui.QWidget()
        self.formPost.resize(800, 640)
        self.formPost.setWindowTitle("Post setup")
        self.formPost.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.formPost)

        # parameters
        self.labelDiameter = QtGui.QLabel()
        self.labelDiameter.setText("Diámetro:")
        self.valueDiameter = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueDiameter.setText("48 mm")
        self.grid.addWidget(self.labelDiameter, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueDiameter, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelLength = QtGui.QLabel()
        self.labelLength.setText("Longitud:")
        self.valueLength = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueLength.setText("3,0 m")
        self.grid.addWidget(self.labelLength, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueLength, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelDepth = QtGui.QLabel()
        self.labelDepth.setText("Profundidad:")
        self.valueDepth = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueDepth.setText("700,0 mm")
        self.grid.addWidget(self.labelDepth, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueDepth, self.grid.rowCount() - 1, 1, 1, 1)

        self.valueDiameter.valueChanged.connect(self.SetupPost)
        self.valueLength.valueChanged.connect(self.SetupPost)
        self.valueDepth.valueChanged.connect(self.SetupPost)

        # Form para configurar la zapata: ----------------------------------------------------------
        self.formFoundation = QtGui.QWidget()
        self.formFoundation.resize(800, 640)
        self.formFoundation.setWindowTitle("Post setup")
        self.formFoundation.setWindowIcon(QtGui.QIcon(os.path.join(DirIcons, "contours.svg")))
        self.grid = QtGui.QGridLayout(self.formFoundation)

        # parameters
        self.labelFoundationDiameter = QtGui.QLabel()
        self.labelFoundationDiameter.setText("Cimentación:")
        self.grid.addWidget(self.labelFoundationDiameter, self.grid.rowCount(), 0, 1, 1)

        self.labelFoundationDiameter = QtGui.QLabel()
        self.labelFoundationDiameter.setText("Diámetro:")
        self.valueFoundationDiameter = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueFoundationDiameter.setText("200,0 mm")
        self.grid.addWidget(self.labelFoundationDiameter, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueFoundationDiameter, self.grid.rowCount() - 1, 1, 1, 1)

        self.labelFoundationDepth = QtGui.QLabel()
        self.labelFoundationDepth.setText("Profundidad:")
        self.valueFoundationDepth = FreeCADGui.UiLoader().createWidget("Gui::InputField")
        self.valueFoundationDepth.setText("700,0 mm")
        self.grid.addWidget(self.labelFoundationDepth, self.grid.rowCount(), 0, 1, 1)
        self.grid.addWidget(self.valueFoundationDepth, self.grid.rowCount() - 1, 1, 1, 1)

        self.form = [self.formFence, self.formPost, self.formFoundation]

        # valores iniciales y creación del la valla:
        import Draft
        self.post = PVPlantFencePost.makeFencePost()  # Arch.makePipe()
        self.post.Label = "Post"
        Draft.autogroup(self.post)

        '''
        self.section = self.makeGrid()
        self.path = self.section.Base
        '''

        FreeCAD.ActiveDocument.recompute()
        self.fence = makePVPlantFence(self.section, self.post, self.path)

    def addPath(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.path = sel[0]
            self.linePath.setText(self.path.Label)
            self.fence.Base = self.path

        FreeCAD.ActiveDocument.recompute()

    def SetupPost(self):
        if self.post.Diameter != FreeCAD.Units.Quantity(self.valueDiameter.text()).Value:
            self.post.Diameter = FreeCAD.Units.Quantity(self.valueDiameter.text()).Value
        if self.post.Length != FreeCAD.Units.Quantity(self.valueLength.text()).Value:
            self.post.Length = FreeCAD.Units.Quantity(self.valueLength.text()).Value

        if self.post.Placement.Base.z != -FreeCAD.Units.Quantity(self.valueDepth.text()).Value:
            self.post.Placement.Base.z = -FreeCAD.Units.Quantity(self.valueDepth.text()).Value
            self.fence.Depth = FreeCAD.Units.Quantity(self.valueDepth.text()).Value

        FreeCAD.ActiveDocument.recompute()

    def SetupGrid(self):
        return
        if self.path.End.x != FreeCAD.Units.Quantity(self.valueInterval.text()).Value:
            self.path.End.x = FreeCAD.Units.Quantity(self.valueInterval.text()).Value
        if self.section.LengthFwd != FreeCAD.Units.Quantity(self.valueHeight.text()).Value:
            self.section.LengthFwd = FreeCAD.Units.Quantity(self.valueHeight.text()).Value

        FreeCAD.ActiveDocument.recompute()

    def makeGrid(self):
        return None

        import Draft

        p1 = FreeCAD.Vector(0, 0, 0)
        p2 = FreeCAD.Vector(4000, 0, 0)
        line = Draft.makeLine(p1, p2)

        section = FreeCAD.ActiveDocument.addObject('Part::Extrusion', 'Extrude')
        section.Base = line
        section.DirMode = "Custom"
        section.Dir = FreeCAD.Vector(0.0, 0.0, 1.0)
        section.DirLink = None
        section.LengthFwd = 2000.0
        section.LengthRev = 0.0
        section.Solid = False
        section.Reversed = False
        section.Symmetric = False
        section.TaperAngle = 0.0
        section.TaperAngleRev = 0.0
        line.Visibility = False

        return section


# Commands ---------------------------------------------------------------------------------
class _CommandPVPlantFenceGate:
    "the PVPlant Fence command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "gate.svg")),
                'Accel': "F, G",
                'MenuText': QT_TRANSLATE_NOOP("PVPlantFenceGate", "Gate"),
                'ToolTip': QT_TRANSLATE_NOOP("PVPlantFence",
                                             "Creates a fence object from a selected section, post and path")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        self.TaskPanel = _FenceGateTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)
