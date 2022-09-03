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
import Part
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from PySide.QtCore import QT_TRANSLATE_NOOP
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

from PVPlantResources import DirIcons as DirIcons

'''
import threading
import datetime

class ThreadClass(threading.Thread):
    def __init__(self, land, Trace):
        self.land = land
        self.trace = Trace

    def run(self):
        tmp = self.land.makeParallelProjection(self.trace, FreeCAD.Vector(0, 0, 1))
        pts = [ver.Point for ver in tmp.Vertexes]
        return pts

        
for i in range(2):
    t = ThreadClass()
    t.start()
'''


def makeTrace(points = None, label = "Trace"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Trace")
    obj.Label = label
    Trace(obj)
    ViewProviderTrace(obj.ViewObject)
    if points:
        obj.Points = points
    return obj


class Trace:
    def __init__(self, obj):
        self.setCommonProperties(obj)

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList
        if not ("Points" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "Points",
                            "PlacementLine",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        if not ("ProjectionPoints" in pl):
            obj.addProperty("App::PropertyVectorList",
                            "ProjectionPoints",
                            "PlacementLine",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            )

        if not ("ShowTrend" in pl):
            obj.addProperty("App::PropertyBool",
                            "ShowTrend",
                            "PlacementLine",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).ShowTrend = True

        self.Type = "TraceLine"
        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''Do something when a property has changed'''

    def execute(self, obj):
        if len(obj.Points) > 1:
            obj.Shape = Part.makePolygon(obj.Points)

        '''
        if len(obj.ProjectionPoints) > 1 and obj.ShowTrend:
            # TODO: check:
            from scipy import stats
            xx = list()
            yy = list()
            zz = list()

            for pts in obj.ProjectionPoints:
                xx.append(pts.x)
                yy.append(pts.y)
                zz.append(pts.z)

            slope, intercept, r, p, std_err = stats.linregress(yy, zz)

            def myfunc(x):
                return slope * x + intercept

            x = list()
            x.append(yy[0])
            x.append(yy[-1])
            newzz = list(map(myfunc, x))

            for p in range(len(obj.Points) - 1):
                #found = [i for i in map(lambda n: float(n.replace(',', '.')), values) if 1.50 < i < 2.50]
                r = []

                #if obj.Points[p]
                mi = obj.Points[p + 1]
                ma = obj.Points[p]
                for p3d in obj.ProjectionPoints:
                    if mi.x <= p3d.x <= ma.x and mi.y <= p3d.y <= ma.y:
                        r.append(p3d)

                tmp = Part.makePolygon([FreeCAD.Vector(xx[0], yy[0], newzz[0]),
                                        FreeCAD.Vector(xx[-1], yy[-1], newzz[-1])])
                #obj.Shape = obj.Shape.fuse([tmp,])
        '''


class ViewProviderTrace:
    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = None
        self.editor = None
        self.select_state = True
        self.active = False
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        self.active = False
        self.select_state = vobj.Selectable
        self.ip = None
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''

        return str(os.path.join(DirIcons, "Trace.svg"))

    def setEdit(self, vobj, mode=0):
        """Method called when the document requests the object to enter edit mode.

        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].

        Just display the standard Point Edit task panel.

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
            import Utils.profile_editor as editor
            if vobj.Selectable:
                self.select_state = True
                vobj.Selectable = False
            pts = list()
            for i in range(len(self.Object.Points)):
                p = self.Object.Points[i]
                pts.append(editor.MarkerOnShape([p]))
            self.editor = editor.Edit(pts, self.Object)
            for i in range(min(len(self.Object.Shape.Edges), len(self.editor.lines))):
                self.editor.lines[i].updateLine()
            self.active = True
            return True
        return False

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        import Utils.profile_editor as editor
        if isinstance(self.editor, editor.Edit):# and check_pivy():
            pts = list()
            for p in self.editor.points:
                if isinstance(p, editor.MarkerOnShape):
                    pt = p.points[0]
                    pts.append(FreeCAD.Vector(pt[0], pt[1], pt[2]))
            self.Object.Points = pts
            vobj.Selectable = self.select_state
            self.editor.quit()
        del self.editor
        self.editor = None
        self.active = False
        self.Object.Document.recompute()
        return True

    def doubleClicked(self, vobj):
        if not hasattr(self, 'active'):
            self.active = False
        if not self.active:
            self.active = True
            # self.setEdit(vobj)
            vobj.Document.setEdit(vobj)
        else:
            vobj.Document.resetEdit()
            self.active = False
        return True

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        return None

class CommandTrace:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "Trace.svg")),
                'Accel': "T, R",
                'MenuText': "Trace",
                'ToolTip': "Trace"}

    def Activated(self):
        points = None
        '''
        sel = FreeCADGui.Selection.getSelection()
        if sel:
            points = sel[0].Points
        '''
        obj = makeTrace(points)
        #obj.ViewObject.Document.setEdit(obj.ViewObject)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('Trace', CommandTrace())