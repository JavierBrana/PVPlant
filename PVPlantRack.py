import FreeCAD, Draft
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

    import Part
    import pivy
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

__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")
DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")

class _Frame(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setCommonProperties(obj)

        # Does a IfcType exist?
        obj.IfcType = "Structural Item"
        obj.setEditorMode("IfcType", 1)
        # obj.MoveWithHost = False

        self.totalAreaShape = None

        self.ModuleArea = []
        self.ListModules = []
        self.ListPosts = []
        self.changed = True

    def setCommonProperties(self, obj):
        # Definicion de Propiedades:
        ArchComponent.Component.setProperties(self, obj)

        # Modulo: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "ModuleThick",
                        "Module",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).ModuleThick = 40

        obj.addProperty("App::PropertyLength",
                        "ModuleWidth",
                        "Module",
                        QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                        ).ModuleWidth = 992

        obj.addProperty("App::PropertyLength",
                        "ModuleHeight",
                        "Module",
                        QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                        ).ModuleHeight = 1996

        obj.addProperty("App::PropertyQuantity",
                        "ModulePower",
                        "Module",
                        QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                        ).ModulePower = 400

        # Array de modulos: -------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyQuantity",
                        "ModuleCols",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).ModuleCols = 15

        obj.addProperty("App::PropertyQuantity",
                        "ModuleRows",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).ModuleRows = 2

        obj.addProperty("App::PropertyDistance",
                        "ModuleColGap",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).ModuleColGap = 20

        obj.addProperty("App::PropertyDistance",
                        "ModuleRowGap",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).ModuleRowGap = 20

        obj.addProperty("App::PropertyDistance",
                       "ModuleOffsetX",
                       "Posicion de modulos",
                       QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                       ).ModuleOffsetX = 0

        obj.addProperty("App::PropertyDistance",
                       "ModuleOffsetY",
                       "Posicion de modulos",
                       QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                       ).ModuleOffsetY = 0

        obj.addProperty("App::PropertyEnumeration",
                        "ModuleOrientation",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "The facemaker type to use to build the profile of this object")
                        ).ModuleOrientation = ["Portrait", "Landscape"]

        obj.addProperty("App::PropertyBool",
                        "ModuleViews",
                        "Posicion de modulos",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "The facemaker type to use to build the profile of this object")
                        ).ModuleViews = True

        # Frame --------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyAngle",
                        "Tilt",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).Tilt = 30

        obj.addProperty("App::PropertyAngle",
                        "MaxLengthwiseTilt",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property", "Máxima inclinación longitudinal")
                        ).MaxLengthwiseTilt = 15

        obj.addProperty("App::PropertyDistance",
                        "Width",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Largo de la estructura")
                        )
        obj.setEditorMode("Width", 1)

        obj.addProperty("App::PropertyDistance",
                        "Length",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property",
                                          "Ancho de la estructura")
                        )
        obj.setEditorMode("Length", 1)

        obj.addProperty("App::PropertyDistance",
                        "TotalAreaShape",
                        "Frame",
                        QT_TRANSLATE_NOOP("Part::PropertyPartShape",
                                          "Total Area de los Paneles")
                        )
        obj.setEditorMode("TotalAreaShape", 1)
        self.Type = "Frame"

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
                 'Sketcher::PropertyConstraintList']
        '''

    def getTotalAreaShape(self):
        return self.totalAreaShape

''' ------------------------------------------- Fixed Structure --------------------------------------------------- '''
def makeRack(objectslist=None, baseobj=None, name="Rack"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Rack")
    _FixedRack(obj)
    _ViewProviderFixedRack(obj.ViewObject)
    #FreeCAD.ActiveDocument.recompute()
    return obj


class _FixedRack(_Frame):
    "A Fixed Rack Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        _Frame.__init__(self, obj)
        _Frame.setProperties(self, obj)
        self.setProperties(obj)
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False

    def setProperties(self, obj):
        # Definicion de Propiedades:

        # Array of Posts: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyQuantity",
                        "NumberPostsX",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).NumberPostsX = 5

        obj.addProperty("App::PropertyLength",
                        "DistancePostsX",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).DistancePostsX = 3000

        obj.addProperty("App::PropertyBool",
                        "FrontPost",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).FrontPost = False

        obj.addProperty("App::PropertyLength",
                        "DistancePostsY",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).DistancePostsY = 2000

        obj.addProperty("App::PropertyLength",
                        "RammingDeep",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).RammingDeep = 1500
        # Correas: ----------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "BeamHeight",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamHeight = 80

        obj.addProperty("App::PropertyLength",
                        "BeamWidth",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                        ).BeamWidth = 50

        obj.addProperty("App::PropertyLength",
                        "BeamOffset",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamOffset = 50

        obj.addProperty("App::PropertyLength",
                        "BeamSpacing",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamSpacing = 1000


        self.Type = "Fixed Rack"

    def onDocumentRestored(self, obj):
        ArchComponent.Component.onDocumentRestored(self, obj)
        # self.setProperties(obj)
        self.Type = "Fixed Rack"

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    '''
    def addObject(self, child):
        print("addObject")

    def removeObject(self, child):
        print("removeObject")

    def onChanged(self, obj, prop):
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
    '''

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def CalculateModuleArray(self, obj, totalh, totalw, moduleh, modulew):
        # ModuleThick
        # ModuleWidth
        # ModuleThinness
        # ModuleColor
        # ModuleCols
        # ModuleRows
        # ModuleColGap
        # ModuleRowGap

        # BeamHeight
        # BeamWidth
        # BeamOffset

        import Part, Draft

        # pl = obj.Placement
        module = Part.makeBox(modulew, moduleh, obj.ModuleThick.Value)
        correa = Part.makeBox(totalw + obj.BeamOffset.Value * 2, obj.BeamWidth.Value, obj.BeamHeight.Value)

        # Longitud poste - Produndidad de hincado + correas
        correaoffsetz = obj.BackPostLength.Value
        offsetz = correaoffsetz + obj.BeamHeight.Value

        p1 = FreeCAD.Vector(0, 0, 0)
        p2 = FreeCAD.Vector(totalw, 0, 0)
        p3 = FreeCAD.Vector(totalw, totalh, 0)
        p4 = FreeCAD.Vector(0, totalh, 0)
        polygon = Part.makePolygon([p1, p2, p3, p4, p1])
        totalArea = Part.makeFilledFace(polygon.Edges)
        totalArea.Placement.Base.x = -totalw / 2
        totalArea.Placement.Base.y = -totalh / 2
        totalArea.Placement.Base.z = obj.BeamHeight.Value

        self.ModuleArea = totalArea
        # if ShowtotalArea:
        self.ListModules.append(totalArea)

        correaoffsety = (moduleh - obj.BeamSpacing.Value - obj.BeamWidth.Value) / 2
        for y in range(int(obj.ModuleRows.Value)):
            # Correas
            '''
            for i in range(2):
                correaCopy = correa.copy()
                correaCopy.Placement.Base.x = totalArea.Placement.Base.x - obj.BeamWidth.Value
                correaCopy.Placement.Base.y = totalArea.Placement.Base.y + correaoffsety + (obj.BeamSpacing.Value * i) + (
                            moduleh + obj.ModuleRowGap.Value) * y
                self.ListModules.append(correaCopy)
            '''
            # Módulos
            for x in range(int(obj.ModuleCols.Value)):
                xx = totalArea.Placement.Base.x + (modulew + obj.ModuleColGap.Value) * x
                yy = totalArea.Placement.Base.y + (moduleh + obj.ModuleRowGap.Value) * y
                zz = obj.BeamHeight.Value
                moduleCopy = module.copy()
                moduleCopy.Placement.Base.x = xx
                moduleCopy.Placement.Base.y = yy
                moduleCopy.Placement.Base.z = zz
                self.ListModules.append(moduleCopy)

        compound = Part.makeCompound(self.ListModules)
        compound.Placement.Base.z = correaoffsetz - obj.RammingDeep.Value

        if obj.FrontPost:
            base = FreeCAD.Vector(0, (-obj.BackPostHeight.Value + obj.DistancePostsY.Value) / 2,
                                  correaoffsetz - obj.RammingDeep.Value)
        else:
            base = FreeCAD.Vector(0, -obj.BackPostHeight.Value / 2 + totalh / 3,
                                  correaoffsetz - obj.RammingDeep.Value)

        a = compound.rotate(base, FreeCAD.Vector(1, 0, 0), obj.Tilt)

        del correa
        del module
        del compound
        del self.ListModules[:]

        self.ListModules.append(a)

    def CalculatePosts(self, obj, totalh, totalw):
        '''
        # NumberPostsX
        # NumberPostsY
        # PostHeight
        # PostWidth
        # PostLength
        # DistancePostsX
        # DistancePostsY
        '''

        import Part, math
        postBack = Part.makeBox(obj.BackPostWidth.Value, obj.BackPostHeight.Value, obj.BackPostLength.Value)
        postFront = Part.makeBox(obj.FrontPostWidth.Value, obj.FrontPostHeight.Value, obj.FrontPostLength.Value)

        angle = obj.Placement.Rotation.toEuler()[1]
        offsetX = (-obj.DistancePostsX.Value * (obj.NumberPostsX.Value - 1)) / 2

        # offsetY = (-obj.PostHeight.Value - obj.DistancePostsY * (obj.NumberPostsY - 1)) / 2
        if obj.FrontPost:
            offsetY = (-obj.BackPostHeight.Value + obj.DistancePostsY.Value) / 2
        else:
            # TODO: cambiar el totalh / 3 por el valor adecuado
            offsetY = -obj.BackPostHeight.Value / 2 + totalh / 3

        offsetZ = -obj.RammingDeep.Value

        for x in range(int(obj.NumberPostsX.Value)):
            xx = offsetX + (obj.NumberPostsX.Value + obj.DistancePostsX.Value) * x #* math.cos(obj.Placement.Rotation.toEuler()[1])
            yy = offsetY
            zz = offsetZ #* math.sin(obj.Placement.Rotation.toEuler()[1])

            postCopy = postBack.copy()
            postCopy.Placement.Base.x = xx
            postCopy.Placement.Base.y = yy
            postCopy.Placement.Base.z = zz
            base = FreeCAD.Vector(xx, yy, obj.BackPostHeight.Value - offsetZ)
            postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
            self.ListPosts.append(postCopy)

            if obj.FrontPost:
                postCopy = postFront.copy()
                postCopy.Placement.Base.x =  xx
                postCopy.Placement.Base.y = -yy
                postCopy.Placement.Base.z =  zz
                base = FreeCAD.Vector(xx, yy, obj.FrontPostHeight.Value - offsetZ)
                postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
                self.ListPosts.append(postCopy)

        del postBack
        del postFront

    def execute(self, obj):

        pl = obj.Placement

        del self.ListModules[:]
        del self.ListPosts[:]

        self.ListModules = []
        self.ListPosts = []

        if obj.ModuleOrientation == "Portrait":
            w = obj.ModuleWidth.Value
            h = obj.ModuleHeight.Value
        else:
            h = obj.ModuleWidth.Value
            w = obj.ModuleHeight.Value

        totalh = h * obj.ModuleRows + obj.ModuleRowGap.Value * (obj.ModuleRows - 1)
        totalw = w * obj.ModuleCols + obj.ModuleColGap.Value * (obj.ModuleCols - 1)
        obj.Width = totalw
        obj.Length = totalh


        # hacer el shape:
        self.CalculateModuleArray(obj, totalh, totalw, h, w)
        self.CalculatePosts(obj, totalh, totalw)

        allShapes = []
        allShapes.extend(self.ListModules)
        allShapes.extend(self.ListPosts)
        compound = Part.makeCompound(allShapes)
        obj.Shape = compound
        obj.Placement = pl

        angle = obj.Placement.Rotation.toEuler()[1]
        if angle > obj.MaxLengthwiseTilt:
            obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
        print("fin")

class _ViewProviderFixedRack(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)
        '''
        ArchSite._ViewProviderSite.__init__(self, vobj)
        vobj.Proxy = self
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        self.setProperties(vobj)
        '''

    def getIcon(self):
        """ Return the path to the appropriate icon. """
        return str(os.path.join(DirIcons, "solar-fixed.svg"))

    def setEdit(self, vobj, mode):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard Arch component task panel.

        Parameters
        ----------
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].

        Returns
        -------
        bool
            If edit mode was entered.
        """

        if (mode == 0) and hasattr(self, "Object"):
            taskd = _FixedRackTaskPanel(self.Object)
            taskd.obj = self.Object
            FreeCADGui.Control.showDialog(taskd)
            return True

        return False

class _FixedRackTaskPanel:
    def __init__(self, obj=None):
        self.obj = obj

        # -------------------------------------------------------------------------------------------------------------
        # Module widget form
        # -------------------------------------------------------------------------------------------------------------
        self.formRack = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]


    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


''' ------------------------------------------- Tracker Structure --------------------------------------------------- '''


def makeTracker(objectslist=None, baseobj=None, name="Rack"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Tracker")
    _Tracker(obj)
    _ViewProviderTracker(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class _Tracker(_Frame):
    "A 1 Axis Tracker Obcject"

    def __init__(self, obj):
        # Definición de Variables:
        _Frame.__init__(self, obj)
        self.setProperties(obj)
        self.Type = "1 Axis Tracker"
        self.obj = obj
        obj.Proxy = self

        obj.ModuleCols = 45
        obj.ModuleRows = 2
        obj.ModuleColGap = 20
        obj.ModuleRowGap = 20
        obj.Tilt = 0

        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False

    def setProperties(self, obj):
        # Definicion de Propiedades:
        # Array de modulos: -------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyDistance",
                    "MotorGap",
                    "Posicion de modulos",
                    QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                    ).MotorGap = 550

        # Poles: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "PoleHeight",
                        "Pole",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).PoleHeight = 160

        obj.addProperty("App::PropertyLength",
                        "PoleWidth",
                        "Pole",
                        QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                        ).PoleWidth = 80

        obj.addProperty("App::PropertyLength",
                        "PoleLength",
                        "Pole",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).PoleLength = 3000

        # Array of Posts: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyQuantity",
                        "NumberPole",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).NumberPole = 7

        obj.addProperty("App::PropertyFloatList",
                        "DistancePole",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).DistancePole = [1500.0, 3000.0, 7000.0, 7000.0, 7000.0, 7000.0, 7000.0]

        obj.addProperty("App::PropertyLength",
                        "AerialPole",
                        "Poles",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).AerialPole = 1050

        # Correas: ----------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "MainBeamHeight",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).MainBeamHeight = 120

        obj.addProperty("App::PropertyLength",
                        "MainBeamWidth",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).MainBeamWidth = 120

        obj.addProperty("App::PropertyLength",
                        "MainBeamAxisPosition",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).MainBeamAxisPosition = 1278

        obj.addProperty("App::PropertyLength",
                        "BeamHeight",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamHeight = 80

        obj.addProperty("App::PropertyLength",
                        "BeamWidth",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                        ).BeamWidth = 50

        obj.addProperty("App::PropertyLength",
                        "BeamOffset",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamOffset = 50

        obj.addProperty("App::PropertyLength",
                        "BeamSpacing",
                        "Beam",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).BeamSpacing = 1000

        # Tracker --------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyAngle",
                        "MaxPhi",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).MaxPhi = 60

        obj.addProperty("App::PropertyAngle",
                        "MinPhi",
                        "Frame",
                        QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                        ).MinPhi = -60

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and Arch wall properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.obj = obj
        self.Type = "1 Axis Tracker"
        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''

        self.changed = True

        if prop in ["MaxPhi", "MinPhi", ]:
            self.changed = False

        if prop == "Tilt":
            if not hasattr(self, "obj"):
                return
            if hasattr(self.obj, "MaxPhi"):
                if self.obj.Tilt > self.obj.MaxPhi:
                    self.obj.Tilt = self.obj.MaxPhi

                if self.obj.Tilt < self.obj.MinPhi:
                    self.obj.Tilt = self.obj.MinPhi

            compound = self.obj.Shape.SubShapes[0]
            compound.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 45)
            #a = compound.rotate(base, FreeCAD.Vector(1, 0, 0), obj.Tilt)
            self.changed = True

    def CalculateModuleArray(self, obj, totalh, totalw, moduleh, modulew):

        import Part, Draft

        module = Part.makeBox(modulew, moduleh, obj.ModuleThick.Value)
        compound = Part.makeCompound([])
        offsetz = obj.MainBeamHeight.Value + obj.BeamHeight.Value

        # if ShowtotalArea:
        '''
        if obj.MotorGap.Value > 0:
            ox = 0
            ma = (totalw - obj.MotorGap.Value) / 2
            for i in range(0,2):
                p1 = FreeCAD.Vector(ox, 0, 0)
                p2 = FreeCAD.Vector(ma + ox, 0, 0)
                p3 = FreeCAD.Vector(ma + ox, totalh, 0)
                p4 = FreeCAD.Vector(ox, totalh, 0)
                polygon = Part.makePolygon([p1, p2, p3, p4, p1])
                totalArea = Part.makeFilledFace(polygon.Edges)
                totalArea.Placement.Base.x = -totalw / 2
                totalArea.Placement.Base.y = -totalh / 2
                totalArea.Placement.Base.z = offsetz
                self.ModuleAreas.append(totalArea)

                ox += ma + obj.MotorGap.Value
        else:
        '''
        p1 = FreeCAD.Vector(0, 0, 0)
        p2 = FreeCAD.Vector(totalw, 0, 0)
        p3 = FreeCAD.Vector(totalw, totalh, 0)
        p4 = FreeCAD.Vector(0, totalh, 0)
        polygon = Part.makePolygon([p1, p2, p3, p4, p1])
        totalArea = Part.makeFilledFace(polygon.Edges)
        totalArea.Placement.Base.x = -totalw / 2
        totalArea.Placement.Base.y = -totalh / 2
        totalArea.Placement.Base.z = offsetz
        self.ModuleAreas.append(totalArea)
        compound.add(self.ModuleAreas[0])

        mainbeam = Part.makeBox(totalw + obj.ModuleOffsetX.Value * 2, obj.MainBeamWidth.Value, obj.MainBeamHeight.Value)
        mainbeam.Placement.Base.x = -totalw / 2 - obj.ModuleOffsetX.Value
        mainbeam.Placement.Base.y = -obj.MainBeamWidth.Value / 2
        # compound.add(mainbeam)

        if obj.ModuleViews:
            correaoffsety = (moduleh - obj.BeamSpacing.Value - obj.BeamWidth.Value) / 2
            mid = int(obj.ModuleCols.Value / 2)
            for row in range(int(obj.ModuleRows.Value)):
                # Correas
                '''
                for i in range(2):
                    correaCopy = correa.copy()
                    correaCopy.Placement.Base.x = totalArea.Placement.Base.x - obj.BeamWidth.Value
                    correaCopy.Placement.Base.y = totalArea.Placement.Base.y + correaoffsety + (obj.BeamSpacing.Value * i) + (
                                moduleh + obj.ModuleRowGap.Value) * y
                    self.ListModules.append(correaCopy)
                '''
                # Módulos
                for col in range(int(obj.ModuleCols.Value)):
                    xx = totalArea.Placement.Base.x + (modulew + obj.ModuleColGap.Value) * col
                    if col >= mid:
                        xx += float(obj.MotorGap.Value) - obj.ModuleColGap.Value
                    yy = totalArea.Placement.Base.y + (moduleh + obj.ModuleRowGap.Value) * row
                    zz = offsetz
                    moduleCopy = module.copy()
                    moduleCopy.Placement.Base.x = xx
                    moduleCopy.Placement.Base.y = yy
                    moduleCopy.Placement.Base.z = zz
                    self.ListModules.append(moduleCopy)
                    compound.add(moduleCopy)

        compound.Placement.Base.z = obj.MainBeamAxisPosition.Value - (obj.MainBeamHeight.Value / 2)
        base = FreeCAD.Vector(0, 0, obj.MainBeamAxisPosition.Value)
        a = compound.rotate(base, FreeCAD.Vector(1, 0, 0), obj.Tilt)
        #???compound.Placement.Rotation = FreeCAD.Rotation()

        del mainbeam
        del module
        del compound
        del self.ListModules[:]

        self.ListModules.append(a)

    def CalculatePosts(self, obj, totalh, totalw):

        import Part, math
        posttmp = Part.makeBox(obj.PoleWidth.Value, obj.PoleHeight.Value, obj.PoleLength.Value)
        #compound = Part.makeCompound([])

        angle = obj.Placement.Rotation.toEuler()[1]
        offsetX = - totalw / 2
        offsetY = -obj.PoleHeight.Value / 2
        offsetZ = -(obj.PoleLength.Value - obj.AerialPole.Value)

        for x in range(int(obj.NumberPole.Value)):
            offsetX += obj.DistancePole[x] - obj.PoleWidth.Value / 2
            xx = offsetX
            yy = offsetY
            zz = offsetZ

            postCopy = posttmp.copy()
            postCopy.Placement.Base.x = xx
            postCopy.Placement.Base.y = yy
            postCopy.Placement.Base.z = zz
            base = FreeCAD.Vector(xx, yy, obj.PoleHeight.Value - offsetZ)
            postCopy = postCopy.rotate(base, FreeCAD.Vector(0, 1, 0), -angle)
            self.ListPosts.append(postCopy)

    def execute(self, obj):

        if self.changed:
            self.ModuleAreas = []
            self.ListModules = []
            self.ListPosts = []
            self.ListBeams = []

            pl = obj.Placement

            if obj.ModuleOrientation == "Portrait":
                w = obj.ModuleWidth.Value
                h = obj.ModuleHeight.Value
            else:
                h = obj.ModuleWidth.Value
                w = obj.ModuleHeight.Value

            totalh = h * obj.ModuleRows + obj.ModuleRowGap.Value * (obj.ModuleRows - 1)
            totalw = w * obj.ModuleCols + obj.ModuleColGap.Value * (obj.ModuleCols - 1) + \
                     (obj.MotorGap.Value - obj.ModuleColGap.Value) if obj.MotorGap.Value > 0 else 0
            obj.Width = totalw + obj.ModuleOffsetX.Value * 2
            obj.Length = totalh

            # hacer el shape:
            self.CalculateModuleArray(obj, totalh, totalw, h, w)
            self.CalculatePosts(obj, totalh, totalw)

            allShapes = []
            allShapes.extend(self.ListModules)
            allShapes.extend(self.ListPosts)
            compound = Part.makeCompound(allShapes)
            obj.Shape = compound
            obj.Placement = pl

            angle = obj.Placement.Rotation.toEuler()[1]
            if angle > obj.MaxLengthwiseTilt:
                obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)

            self.totalAreaShape = self.ModuleAreas[0]
            #obj.TotalAreaShape = self.ModuleAreas[0].Shape

            del self.ModuleAreas[:]
            del self.ListModules[:]
            del self.ListPosts[:]
            del allShapes[:]
            self.changed = False


class _ViewProviderTracker(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "solar-tracker.svg"))

    def setEdit(self, vobj, mode):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard Arch component task panel.

        Parameters
        ----------
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].

        Returns
        -------
        bool
            If edit mode was entered.
        """

        if (mode == 0) and hasattr(self, "Object"):
            taskd = _TrackerTaskPanel(self.Object)
            taskd.obj = self.Object
            #taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True

        return False




class _TrackerTaskPanel:
    def __init__(self, obj=None):

        if not (obj is None):
            self.new = True
            self.ojb = makeRack()
        else:
            self.new = False
            self.obj = obj

        # -------------------------------------------------------------------------------------------------------------
        # Module widget form
        # -------------------------------------------------------------------------------------------------------------
        self.formRack = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        if self.new:
            FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True






class _FrameTaskPanel:

    def __init__(self, obj=None):

        if not (obj is None):
            self.new = True
            self.ojb = makeRack()
        else:
            self.new = False
            self.obj = obj

        self.formRack = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.setEnable(self.new)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")
        self.formPiling.editBreadthwaysNumOfPost.valueChanged.connect(self.editBreadthwaysNumOfPostChange)
        self.formPiling.editAlongNumOfPost.valueChanged.connect(self.editAlongNumOfPostChange)

        self.form = [self.formRack, self.formPiling]

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True
        self.formRack.widgetTracker.setVisible(vis)

    def editBreadthwaysNumOfPostChange(self):
        self.formPiling.tableBreadthwaysPosts.insertRow(self.formPiling.tableBreadthwaysPosts.rowCount)

    def editAlongNumOfPostChange(self):
        self.l1.setText("current value:" + str(self.sp.value()))

    def getValues(self):
        d = {}
        d["ModuleFrame"] = self.ModuleFrame
        d["ModuleHeight"] = self.ModuleHeight
        d["ModuleWidth"] = self.ModuleWidth
        d["ModuleThick"] = self.ModuleThick
        return d

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        if self.new:
            FreeCADGui.Control.closeDialog()
        return True


class _CommandFixedRack:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-fixed.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantRack", "Fixed Rack"),
                'Accel': "R, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantRack",
                                                    "Creates a Fixed Rack object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        obj = makeRack()
        self.TaskPanel = _FixedRackTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return


class _CommandTracker:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-tracker.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTracker", "Tracker"),
                'Accel': "R, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTracker",
                                                    "Creates a Tracker object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        obj = makeTracker()
        self.TaskPanel = _FixedRackTaskPanel(obj)
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return


if FreeCAD.GuiUp:
    class CommandRackGroup:

        def GetCommands(self):
            return tuple(['PVPlantFixedRack',
                          'PVPlantTracker'
                          ])

        def GetResources(self):
            return {'MenuText': QT_TRANSLATE_NOOP("", 'Rack Types'),
                    'ToolTip': QT_TRANSLATE_NOOP("", 'Rack Types')
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None


    FreeCADGui.addCommand('PVPlantFixedRack', _CommandFixedRack())
    FreeCADGui.addCommand('PVPlantTracker', _CommandTracker())
    FreeCADGui.addCommand('RackType', CommandRackGroup())


    '''# -*- coding: utf-8 -*-
# http://forum.freecadweb.org/viewtopic.php?f=22&t=16079
# creer une face autour des objets et la selectionner (ex rectangle face=true)
edges = []
for o in App.ActiveDocument.Objects:
#    print o.TypeId
    if str(o) !=  "<group object>":
        print o.Shape.ShapeType
        if (o.Shape.ShapeType == 'Edge') or (o.Shape.ShapeType == 'Wire'):
            edges.append(o.Shape)

fusion_wire = edges[0]
for no, e in enumerate(edges):
    no += 1
    if no > 1:
        fusion_wire = fusion_wire.fuse(e)

ex = fusion_wire.extrude(FreeCAD.Vector(0,0,5))
FreeCAD.ActiveDocument.recompute()

sel = FreeCADGui.Selection.getSelection()
#print str(sel[0].Shape.ShapeType)
slab = App.ActiveDocument.getObject(sel[0].Name).Shape.cut(ex)

for f in slab.Faces:
    Part.show(f)'''
