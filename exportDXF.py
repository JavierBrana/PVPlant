
import FreeCAD
import ArchComponent
import PVPlantSite
import copy
import Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "PVPlant Export to DXF"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons
from PVPlantResources import DirDocuments as DirDocuments
import ezdxf

'''
add layer:

doc = ezdxf.new(setup=True)  # setup required line types

'''

class exportDXF:
    LINETYPES = [
        'CONTINUOUS', 'CENTER', 'CENTERX2', 'CENTER2',
        'DASHED', 'DASHEDX2', 'DASHED2', 'PHANTOM', 'PHANTOMX2',
        'PHANTOM2', 'DASHDOT', 'DASHDOTX2', 'DASHDOT2', 'DOT',
        'DOTX2', 'DOT2', 'DIVIDE', 'DIVIDEX2', 'DIVIDE2',
    ]

    def __init__(self, filename):
        ''' '''
        self.doc = None
        self.msp = None
        self.filename = filename

        '''
        doc.linetypes.add("GRENZE2",
                          # linetype definition in acad.lin:
                          # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
                          # replacing BOX by shape index 132 (got index from an AutoCAD file),
                          # ezdxf can't get shape index from ltypeshp.shx
                          pattern="A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
                          description="Grenze eckig ----[]-----[]----[]-----[]----[]--",
                          length=1.45,  # required for complex line types
        })
        
        doc.linetypes.add("GRENZE2",
                        # linetype definition in acad.lin:
                        # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
                        # replacing BOX by shape index 132 (got index from an AutoCAD file),
                        # ezdxf can't get shape index from ltypeshp.shx
                        pattern = "A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
                        description = "Límite1 ----0-----0----0-----0----0-----0--",
                        length = 1.45,  # required for complex line types
         })
         '''

    def createFile(self, version = 'R2018'):
        import ezdxf
        # 1. Create a new document
        self.doc = ezdxf.new(version)
        # 2. Setup document:
        self.doc.header["$INSUNITS"] = 6
        self.doc.header['$MEASUREMENT'] = 1
        self.doc.header['$LUNITS'] = 2
        self.doc.header['$AUNITS'] = 0

        # 3. Add new entities to the modelspace:
        self.msp = self.doc.modelspace()

    def saveFile(self):
        from os.path import exists
        file_exists = exists(self.filename)
        self.doc.saveas(self.filename)
        self.doc.save()

    def createLayer(self, layerName = "newLayer", layerColor = 7, layerType = 'CONTINUOUS'):
        self.doc.layers.add(name = layerName, color = layerColor, linetype = layerType)

    def createBlock(self, blockName = 'newBlock'):
        # Create a block
        block = self.doc.blocks.new(name = blockName)

        # Add DXF entities to the block 'FLAG'.
        # The default base point (= insertion point) of the block is (0, 0).
        block.add_lwpolyline([(0, 0), (0, 5), (4, 3), (0, 3)])  # the flag symbol as 2D polyline
        block.add_circle((0, 0), .4, dxfattribs={'color': 2})  # mark the base point with a circle
        return block

    def insertBlock(self):
        point = (0, 0)
        #blk = doc.blocks.get("NAME")
        msp.add_blockref('FLAG', point, dxfattribs={
            'xscale': random_scale,
            'yscale': random_scale,
            'rotation': -15
        })
        msp.add_line((0, 0), (10, 0), dxfattribs={"layer": "MyLines"})




'''    
print("---------- export to dxf ----------")
from ezdxf.math import Vector

DXFFILE = os.path.join(DirDocuments, "template.dxf")
OUTFILE = 'encircle.dxf'

dwg = ezdxf.readfile(DXFFILE)
msp = dwg.modelspace()
dwg.layers.new(name='MyCircles', dxfattribs={'color': 4})

def get_first_circle_center(block_layout):
    block = block_layout.block
    base_point = Vector(block.dxf.base_point)
    circles = block_layout.query('CIRCLE')
    if len(circles):
        circle = circles[0]  # take first circle
        center = Vector(circle.dxf.center)
        return center - base_point
    else:
        return Vector(0, 0, 0)

# block definition to examine
block_layout = dwg.blocks.get('WB')
offset = get_first_circle_center(block_layout)

for e in msp.query('INSERT[name=="WB"]'):
    scale = e.get_dxf_attrib('xscale', 1)  # assume uniform scaling
    _offset = offset.rotate_deg(e.get_dxf_attrib('rotation', 0)) * scale
    location = e.dxf.insert + _offset

    msp.add_circle(center=location, radius=1, dxfattribs={'layer': 'MyCircles'})

dwg.saveas(OUTFILE)
'''

class _PVPlantExportDXF(QtGui.QWidget):
    '''The editmode TaskPanel to select what you want to export'''

    def __init__(self):
        #super(_PVPlantExportDXF, self).__init__()
        QtGui.QWidget.__init__(self)

        # self.form:
        self = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "exportDXF.ui"))
        #setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "convert.svg")))
        #self.form.buttonTo.clicked.connect(self.addTo)

        path = os.path.join(os.path.dirname(FreeCAD.ActiveDocument.FileName), "outputs", "autocad")
        if not os.path.exists(path):
            os.makedirs(path)
        filename = os.path.join(path, FreeCAD.ActiveDocument.Name) + ".dxf"
        self.exporter = exportDXF(filename)

    def writeArea(self):
        ''' '''

    def writeFrames(self):
        blockpanel = self.exporter.createBlock("Panel")
        blockpanel.add_lwpolyline([(0, 0), (0, 5), (4, 3), (0, 3)])

        blockprofile = self.exporter.createBlock("Profile")
        blockprofile.add_circle((0, 0), .4, dxfattribs={'color': 2})
        blockprofile.add_line((0, 0), (10, 0), dxfattribs={"layer": "MyLines"})
        blockprofile.add_line((0, 0), (10, 0), dxfattribs={"layer": "MyLines"})

        for config in FreeCAD.Site.Frames:
            ''' '''
            print(config)
            # 1. Create block:

            # 2. Write frames:


class _CommandExportDXF:
    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "dxf.svg")),
                'Accel': "E, A",
                'MenuText': "Export to DXF",
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Export choosed layers to dxf")}

    def Activated(self):
        taskd = _PVPlantExportDXF()
        taskd.setParent(FreeCADGui.getMainWindow())
        taskd.setWindowFlags(QtCore.Qt.Window)
        taskd.show()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('exportDXF', _CommandExportDXF())

