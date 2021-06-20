import sys
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui
import DraftVecUtils
import draftutils.utils as utils
import draftutils.gui_utils as gui_utils
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils

from draftutils.messages import _msg, _err
from draftutils.translate import translate


class _wire3D(gui_base_original.Creator):
    """Gui command for the Line tool."""

    def __init__(self):
        super(_wire3D, self).__init__()

    def GetResources(self):
        """Set icon, menu and tooltip."""

        return {'Pixmap': 'Draft_Line',
                'Accel': "L,I",
                'MenuText': QT_TRANSLATE_NOOP("Draft_Line", "Line"),
                'ToolTip': QT_TRANSLATE_NOOP("Draft_Line",
                                             "Creates a 2-point line. CTRL to snap, SHIFT to constrain.")}

    def Activated(self, name=translate("draft", "Line")):
        """Execute when the command is called."""
        super(_wire3D, self).Activated(name)

        if not self.doc:
            return
        self.obj = None  # stores the temp shape
        self.oldWP = None  # stores the WP if we modify it
        self.ui.wireUi(name)
        self.ui.setTitle(translate("draft", "Line"))

        if sys.version_info.major < 3:
            if isinstance(self.featureName, unicode):
                self.featureName = self.featureName.encode("utf8")

        self.obj = self.doc.addObject("Part::Feature", self.featureName)
        gui_utils.format_object(self.obj)

        self.call = self.view.addEventCallback("SoEvent", self.action)
        _msg(translate("draft", "Pick first point"))

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """
        print(arg, " -- point: ", gui_tool_utils.getPoint(self, arg))

        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            if arg["Position"] == self.pos:
                return self.finish(False, cont=True)
            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)

            if self.point:
                self.point = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])
                self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawSegment(self.point)
                if len(self.node) > 2:
                    # The wire is closed
                    if (self.point - self.node[0]).Length < utils.tolerance():
                        self.undolast()
                        if len(self.node) > 2:
                            self.finish(True, cont=True)
                        else:
                            self.finish(False, cont=True)

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the polyline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        self.removeTemporaryObject()
        if self.oldWP:
            App.DraftWorkingPlane = self.oldWP
            if hasattr(Gui, "Snapper"):
                Gui.Snapper.setGrid()
                Gui.Snapper.restack()
        self.oldWP = None

        if len(self.node) > 1:
            Gui.addModule("Draft")
            # The command to run is built as a series of text strings
            # to be committed through the `draftutils.todo.ToDo` class.
            if (len(self.node) == 2
                    and utils.getParam("UsePartPrimitives", False)):
                # Insert a Part::Primitive object
                p1 = self.node[0]
                p2 = self.node[-1]

                _cmd = 'FreeCAD.ActiveDocument.'
                _cmd += 'addObject("Part::Line", "Line")'
                _cmd_list = ['line = ' + _cmd,
                             'line.X1 = ' + str(p1.x),
                             'line.Y1 = ' + str(p1.y),
                             'line.Z1 = ' + str(p1.z),
                             'line.X2 = ' + str(p2.x),
                             'line.Y2 = ' + str(p2.y),
                             'line.Z2 = ' + str(p2.z),
                             'Draft.autogroup(line)',
                             'FreeCAD.ActiveDocument.recompute()']
                self.commit(translate("draft", "Create Line"),
                            _cmd_list)
            else:
                # Insert a Draft line
                rot, sup, pts, fil = self.getStrings()

                _base = DraftVecUtils.toString(self.node[0])
                _cmd = 'Draft.makeWire'
                _cmd += '('
                _cmd += 'points, '
                _cmd += 'placement=pl, '
                _cmd += 'closed=' + str(closed) + ', '
                _cmd += 'face=' + fil + ', '
                _cmd += 'support=' + sup
                _cmd += ')'
                _cmd_list = ['pl = FreeCAD.Placement()',
                             'pl.Rotation.Q = ' + rot,
                             'pl.Base = ' + _base,
                             'points = ' + pts,
                             'line = ' + _cmd,
                             'Draft.autogroup(line)',
                             'FreeCAD.ActiveDocument.recompute()']
                self.commit(translate("draft", "Create Wire"),
                            _cmd_list)
        super(_wire3D, self).finish()
        if self.ui and self.ui.continueMode:
            self.Activated()

    def removeTemporaryObject(self):
        """Remove temporary object created."""
        if self.obj:
            try:
                old = self.obj.Name
            except ReferenceError:
                # object already deleted, for some reason
                pass
            else:
                todo.ToDo.delay(self.doc.removeObject, old)
        self.obj = None

    def undolast(self):
        """Undoes last line segment."""
        import Part
        if len(self.node) > 1:
            self.node.pop()
            # last = self.node[-1]
            if self.obj.Shape.Edges:
                edges = self.obj.Shape.Edges
                if len(edges) > 1:
                    newshape = Part.makePolygon(self.node)
                    self.obj.Shape = newshape
                else:
                    self.obj.ViewObject.hide()
                # DNC: report on removal
                # _msg(translate("draft", "Removing last point"))
                _msg(translate("draft", "Pick next point"))

    def drawSegment(self, point):
        """Draws new line segment."""
        import Part
        if self.planetrack and self.node:
            self.planetrack.set(self.node[-1])
        if len(self.node) == 1:
            _msg(translate("draft", "Pick next point"))
        elif len(self.node) == 2:
            last = self.node[len(self.node) - 2]
            newseg = Part.LineSegment(last, point).toShape()
            self.obj.Shape = newseg
            self.obj.ViewObject.Visibility = True
            _msg(translate("draft", "Pick next point"))
        else:
            currentshape = self.obj.Shape.copy()
            last = self.node[len(self.node) - 2]
            if not DraftVecUtils.equals(last, point):
                newseg = Part.LineSegment(last, point).toShape()
                newshape = currentshape.fuse(newseg)
                self.obj.Shape = newshape
            _msg(translate("draft", "Pick next point"))

    def wipe(self):
        """Remove all previous segments and starts from last point."""
        if len(self.node) > 1:
            # self.obj.Shape.nullify()  # For some reason this fails
            self.obj.ViewObject.Visibility = False
            self.node = [self.node[-1]]
            if self.planetrack:
                self.planetrack.set(self.node[0])
            _msg(translate("draft", "Pick next point"))

    def orientWP(self):
        """Orient the working plane."""
        import DraftGeomUtils
        if hasattr(App, "DraftWorkingPlane"):
            if len(self.node) > 1 and self.obj:
                n = DraftGeomUtils.getNormal(self.obj.Shape)
                if not n:
                    n = App.DraftWorkingPlane.axis
                p = self.node[-1]
                v = self.node[-2].sub(self.node[-1])
                v = v.negative()
                if not self.oldWP:
                    self.oldWP = App.DraftWorkingPlane.copy()
                App.DraftWorkingPlane.alignToPointAndAxis(p, n, upvec=v)
                if hasattr(Gui, "Snapper"):
                    Gui.Snapper.setGrid()
                    Gui.Snapper.restack()
                if self.planetrack:
                    self.planetrack.set(self.node[-1])

    def numericInput(self, numx, numy, numz):
        """Validate the entry fields in the user interface.

        This function is called by the toolbar or taskpanel interface
        when valid x, y, and z have been entered in the input fields.
        """
        self.point = App.Vector(numx, numy, numz)
        self.node.append(self.point)
        self.drawSegment(self.point)
        self.ui.setNextFocus()