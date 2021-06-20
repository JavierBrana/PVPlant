import FreeCAD
from FreeCAD import Vector
import Part

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



class _Module(Part.Box):
    def __init__(self):
        obj.addProperty("App::PropertyDistance","Length","Modulo",
                        QT_TRANSLATE_NOOP("App::Property","Length of the rectangle")).Length = 1956
        obj.addProperty("App::PropertyDistance", "Width", "Modulo",
                        QT_TRANSLATE_NOOP("App::Property", "Length of the rectangle")).Width = 996
        obj.addProperty("App::PropertyDistance","Height","Modulo",
                        QT_TRANSLATE_NOOP("App::Property","Height of the rectangle")).Height = 40


    def execute(self, obj):
        import Part
        pl = obj.Placement
        p1 = Vector(-obj.Width.Value/2,-obj.Height.Value/2,0)
        p2 = Vector(obj.Width.Value/2,-obj.Height.Value/2,0)
        p3 = Vector(obj.Width.Value/2,obj.Height.Value/2,0)
        p4 = Vector(-obj.Width.Value/2,obj.Height.Value/2,0)
        p = Part.makePolygon([p1,p2,p3,p4,p1])
        p = Part.Face(p)
        #p.reverse()
        obj.Shape = p
        obj.Placement = pl

