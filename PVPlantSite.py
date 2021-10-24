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

import FreeCAD, Draft, ArchCommands, ArchFloor, math, datetime
import ArchSite

if FreeCAD.GuiUp:
    import FreeCADGui
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

import os
from PVPlantResources import DirIcons as DirIcons

__title__ = "FreeCAD Site"
__author__ = ""
__url__ = "http://www.freecadweb.org"

zone_list = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10", "Z11", "Z12",
             "Z13", "Z14", "Z15", "Z16", "Z17", "Z18", "Z19", "Z20", "Z21", "Z22", "Z23", "Z24",
             "Z25", "Z26", "Z27", "Z28", "Z29", "Z30", "Z31", "Z32", "Z33", "Z34", "Z35", "Z36",
             "Z37", "Z38", "Z39", "Z40", "Z41", "Z42", "Z43", "Z44", "Z45", "Z46", "Z47", "Z48",
             "Z49", "Z50", "Z51", "Z52", "Z53", "Z54", "Z55", "Z56", "Z57", "Z58", "Z59", "Z60"]


def get(origin=FreeCAD.Vector(0, 0, 0)):
    """
    Find the existing Site object
    """
    # Return an existing instance of the same name, if found.
    obj = FreeCAD.ActiveDocument.getObject('Site')

    if obj:
        if obj.Origin == FreeCAD.Vector(0, 0, 0):
            obj.Origin = origin
        return obj

    obj = makePVPlantSite()
    return obj


def PartToWire(part):
    import Part, Draft

    PointList = []
    edges = Part.__sortEdges__(part.Shape.Edges)
    for edge in edges:
        PointList.append(edge.Vertexes[0].Point)
    PointList.append(edges[-1].Vertexes[-1].Point)

    Draft.makeWire(PointList, closed=True, face=None, support=None)


def projectWireOnMesh(Boundary, Mesh):
    import Draft

    use = True
    if use:
        import MeshPart as mp

        plist = mp.projectShapeOnMesh(Boundary.Shape, Mesh, FreeCAD.Vector(0, 0, 1))
        PointList = []
        for pl in plist:
            PointList += pl

        Draft.makeWire(PointList, closed=True, face=None, support=None)
        FreeCAD.activeDocument().recompute()

    else:  ## posible código:
        import MeshPart

        CopyMesh = Mesh.copy()
        Base = CopyMesh.Placement.Base
        CopyMesh.Placement.move(Base.negative())

        CopyShape = Boundary.Shape.copy()
        CopyShape.Placement.move(Base.negative())

        Vec = CopyShape.Edge1.Vertexes[0].Point - CopyShape.Edge1.Vertexes[1].Point
        Vec.x, Vec.y = -(Vec.y), Vec.x

        Section = CopyMesh.crossSections([(CopyShape.Edge1.Vertexes[0].Point, Vec)], 0.000001)
        print(Section)

        for i in Section[0]:
            Pwire = Draft.makeWire(i)
            # Pwire.Placement.move(Base)
            ##SectionGroup.addObject(Pwire)

        FreeCAD.ActiveDocument.recompute()


def makePVPlantSite():
    def createGroup(father, groupname, type = None):
        group = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", groupname)
        group.Label = groupname
        father.addObject(group)
        return group

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Site")
    _PVPlantSite(obj)
    if FreeCAD.GuiUp:
        _ViewProviderSite(obj.ViewObject)

    group = createGroup(obj, "CivilGroup")
    group1 = createGroup(group, "Areas")
    createGroup(group1, "Boundary")
    createGroup(group1, "Offset")
    createGroup(group1, "Exclusion")
    createGroup(group, "Drain")
    createGroup(group, "Earthworks")
    createGroup(group, "Fence")
    createGroup(group, "Foundations")
    createGroup(group, "Pads")
    createGroup(group, "Points")
    createGroup(group, "Roads")

    group = createGroup(obj, "ElectricalGroup")
    group1 = createGroup(group, "AC")
    createGroup(group1, "CableAC")
    group1 = createGroup(group, "DC")
    createGroup(group1, "CableDC")
    createGroup(group1, "StringsSetup")
    createGroup(group1, "Strings")
    createGroup(group1, "StringsBoxes")

    group = createGroup(obj, "MechanicalGroup")
    createGroup(group, "FramesSetup")
    createGroup(group, "Frames")

    return obj


def makeSolarDiagram(longitude, latitude, scale=1, complete=False, tz=None):
    """makeSolarDiagram(longitude,latitude,[scale,complete,tz]):
    returns a solar diagram as a pivy node. If complete is
    True, the 12 months are drawn. Tz is the timezone related to
    UTC (ex: -3 = UTC-3)"""

    oldversion = False
    ladybug = False
    try:
        import ladybug
        from ladybug import location
        from ladybug import sunpath
    except:
        # TODO - remove pysolar dependency
        # FreeCAD.Console.PrintWarning("Ladybug module not found, using pysolar instead. Warning, this will be deprecated in the future\n")
        ladybug = False
        try:
            import pysolar
        except:
            try:
                import Pysolar as pysolar
            except:
                FreeCAD.Console.PrintError("The pysolar module was not found. Unable to generate solar diagrams\n")
                return None
            else:
                oldversion = True
        if tz:
            tz = datetime.timezone(datetime.timedelta(hours=-3))
        else:
            tz = datetime.timezone.utc
    else:
        loc = ladybug.location.Location(latitude=latitude, longitude=longitude, time_zone=tz)
        sunpath = ladybug.sunpath.Sunpath.from_location(loc)

    from pivy import coin

    if not scale:
        return None

    circles = []
    sunpaths = []
    hourpaths = []
    circlepos = []
    hourpos = []

    # build the base circle + number positions
    import Part
    for i in range(1, 9):
        circles.append(Part.makeCircle(scale * (i / 8.0)))
    for ad in range(0, 360, 15):
        a = math.radians(ad)
        p1 = FreeCAD.Vector(math.cos(a) * scale, math.sin(a) * scale, 0)
        p2 = FreeCAD.Vector(math.cos(a) * scale * 0.125, math.sin(a) * scale * 0.125, 0)
        p3 = FreeCAD.Vector(math.cos(a) * scale * 1.08, math.sin(a) * scale * 1.08, 0)
        circles.append(Part.LineSegment(p1, p2).toShape())
        circlepos.append((ad, p3))

    # build the sun curves at solstices and equinoxe
    year = datetime.datetime.now().year
    hpts = [[] for i in range(24)]
    m = [(6, 21), (7, 21), (8, 21), (9, 21), (10, 21), (11, 21), (12, 21)]
    if complete:
        m.extend([(1, 21), (2, 21), (3, 21), (4, 21), (5, 21)])
    for i, d in enumerate(m):
        pts = []
        for h in range(24):
            if ladybug:
                sun = sunpath.calculate_sun(month=d[0], day=d[1], hour=h)
                alt = math.radians(sun.altitude)
                az = 90 + sun.azimuth
            elif oldversion:
                dt = datetime.datetime(year, d[0], d[1], h)
                alt = math.radians(pysolar.solar.GetAltitudeFast(latitude, longitude, dt))
                az = pysolar.solar.GetAzimuth(latitude, longitude, dt)
                az = -90 + az  # pysolar's zero is south, ours is X direction
            else:
                dt = datetime.datetime(year, d[0], d[1], h, tzinfo=tz)
                alt = math.radians(pysolar.solar.get_altitude_fast(latitude, longitude, dt))
                az = pysolar.solar.get_azimuth(latitude, longitude, dt)
                az = 90 + az  # pysolar's zero is north, ours is X direction
            if az < 0:
                az = 360 + az
            az = math.radians(az)
            zc = math.sin(alt) * scale
            ic = math.cos(alt) * scale
            xc = math.cos(az) * ic
            yc = math.sin(az) * ic
            p = FreeCAD.Vector(xc, yc, zc)
            pts.append(p)
            hpts[h].append(p)
            if i in [0, 6]:
                ep = FreeCAD.Vector(p)
                ep.multiply(1.08)
                if ep.z >= 0:
                    if not oldversion:
                        h = 24 - h  # not sure why this is needed now... But it is.
                    if h == 12:
                        if i == 0:
                            h = "SUMMER"
                        else:
                            h = "WINTER"
                        if latitude < 0:
                            if h == "SUMMER":
                                h = "WINTER"
                            else:
                                h = "SUMMER"
                    hourpos.append((h, ep))
        if i < 7:
            sunpaths.append(Part.makePolygon(pts))

    for h in hpts:
        if complete:
            h.append(h[0])
        hourpaths.append(Part.makePolygon(h))

    # cut underground lines
    sz = 2.1 * scale
    cube = Part.makeBox(sz, sz, sz)
    cube.translate(FreeCAD.Vector(-sz / 2, -sz / 2, -sz))
    sunpaths = [sp.cut(cube) for sp in sunpaths]
    hourpaths = [hp.cut(cube) for hp in hourpaths]

    # build nodes
    ts = 0.005 * scale  # text scale
    mastersep = coin.SoSeparator()
    circlesep = coin.SoSeparator()
    numsep = coin.SoSeparator()
    pathsep = coin.SoSeparator()
    hoursep = coin.SoSeparator()
    hournumsep = coin.SoSeparator()
    mastersep.addChild(circlesep)
    mastersep.addChild(numsep)
    mastersep.addChild(pathsep)
    mastersep.addChild(hoursep)
    for item in circles:
        circlesep.addChild(toNode(item))
    for item in sunpaths:
        for w in item.Edges:
            pathsep.addChild(toNode(w))
    for item in hourpaths:
        for w in item.Edges:
            hoursep.addChild(toNode(w))
    for p in circlepos:
        text = coin.SoText2()
        s = p[0] - 90
        s = -s
        if s > 360:
            s = s - 360
        if s < 0:
            s = 360 + s
        if s == 0:
            s = "N"
        elif s == 90:
            s = "E"
        elif s == 180:
            s = "S"
        elif s == 270:
            s = "W"
        else:
            s = str(s)
        text.string = s
        text.justification = coin.SoText2.CENTER
        coords = coin.SoTransform()
        coords.translation.setValue([p[1].x, p[1].y, p[1].z])
        coords.scaleFactor.setValue([ts, ts, ts])
        item = coin.SoSeparator()
        item.addChild(coords)
        item.addChild(text)
        numsep.addChild(item)
    for p in hourpos:
        text = coin.SoText2()
        s = str(p[0])
        text.string = s
        text.justification = coin.SoText2.CENTER
        coords = coin.SoTransform()
        coords.translation.setValue([p[1].x, p[1].y, p[1].z])
        coords.scaleFactor.setValue([ts, ts, ts])
        item = coin.SoSeparator()
        item.addChild(coords)
        item.addChild(text)
        numsep.addChild(item)
    return mastersep


def makeWindRose(epwfile, scale=1, sectors=24):
    """makeWindRose(site,sectors):
    returns a wind rose diagram as a pivy node"""

    try:
        import ladybug
        from ladybug import epw
    except:
        FreeCAD.Console.PrintError("The ladybug module was not found. Unable to generate solar diagrams\n")
        return None
    if not epwfile:
        FreeCAD.Console.PrintWarning("No EPW file, unable to generate wind rose.\n")
        return None
    epw_data = ladybug.epw.EPW(epwfile)
    baseangle = 360 / sectors
    sectorangles = [i * baseangle for i in range(sectors)]  # the divider angles between each sector
    basebissect = baseangle / 2
    angles = [basebissect]  # build a list of central direction for each sector
    for i in range(1, sectors):
        angles.append(angles[-1] + baseangle)
    windsbysector = [0 for i in range(sectors)]  # prepare a holder for values for each sector
    for hour in epw_data.wind_direction:
        sector = min(angles, key=lambda x: abs(x - hour))  # find the closest sector angle
        sectorindex = angles.index(sector)
        windsbysector[sectorindex] = windsbysector[sectorindex] + 1
    maxwind = max(windsbysector)
    windsbysector = [wind / maxwind for wind in windsbysector]  # normalize
    vectors = []  # create 3D vectors
    dividers = []
    for i in range(sectors):
        angle = math.radians(90 + angles[i])
        x = math.cos(angle) * windsbysector[i] * scale
        y = math.sin(angle) * windsbysector[i] * scale
        vectors.append(FreeCAD.Vector(x, y, 0))
        secangle = math.radians(90 + sectorangles[i])
        x = math.cos(secangle) * scale
        y = math.sin(secangle) * scale
        dividers.append(FreeCAD.Vector(x, y, 0))
    vectors.append(vectors[0])

    # build coin node
    import Part
    from pivy import coin
    masternode = coin.SoSeparator()
    for r in (0.25, 0.5, 0.75, 1.0):
        c = Part.makeCircle(r * scale)
        masternode.addChild(toNode(c))
    for divider in dividers:
        l = Part.makeLine(FreeCAD.Vector(), divider)
        masternode.addChild(toNode(l))
    ds = coin.SoDrawStyle()
    ds.lineWidth = 2.0
    masternode.addChild(ds)
    d = Part.makePolygon(vectors)
    masternode.addChild(toNode(d))
    return masternode


# Values in mm
COMPASS_POINTER_LENGTH = 1000
COMPASS_POINTER_WIDTH = 100


class Compass(object):
    def __init__(self):
        self.rootNode = self.setupCoin()

    def show(self):
        from pivy import coin
        self.compassswitch.whichChild = coin.SO_SWITCH_ALL

    def hide(self):
        from pivy import coin
        self.compassswitch.whichChild = coin.SO_SWITCH_NONE

    def rotate(self, angleInDegrees):
        from pivy import coin
        self.transform.rotation.setValue(
            coin.SbVec3f(0, 0, 1), math.radians(angleInDegrees))

    def locate(self, x, y, z):
        from pivy import coin
        self.transform.translation.setValue(x, y, z)

    def scale(self, area):
        from pivy import coin

        scale = round(max(math.sqrt(area.getValueAs("m^2").Value) / 10, 1))

        self.transform.scaleFactor.setValue(coin.SbVec3f(scale, scale, 1))

    def setupCoin(self):
        from pivy import coin

        compasssep = coin.SoSeparator()

        self.transform = coin.SoTransform()

        darkNorthMaterial = coin.SoMaterial()
        darkNorthMaterial.diffuseColor.set1Value(
            0, 0.5, 0, 0)  # north dark color

        lightNorthMaterial = coin.SoMaterial()
        lightNorthMaterial.diffuseColor.set1Value(
            0, 0.9, 0, 0)  # north light color

        darkGreyMaterial = coin.SoMaterial()
        darkGreyMaterial.diffuseColor.set1Value(0, 0.9, 0.9, 0.9)  # dark color

        lightGreyMaterial = coin.SoMaterial()
        lightGreyMaterial.diffuseColor.set1Value(
            0, 0.5, 0.5, 0.5)  # light color

        coords = self.buildCoordinates()

        # coordIndex = [0, 1, 2, -1, 2, 3, 0, -1]

        lightColorFaceset = coin.SoIndexedFaceSet()
        lightColorCoordinateIndex = [4, 5, 6, -1, 8, 9, 10, -1, 12, 13, 14, -1]
        lightColorFaceset.coordIndex.setValues(
            0, len(lightColorCoordinateIndex), lightColorCoordinateIndex)

        darkColorFaceset = coin.SoIndexedFaceSet()
        darkColorCoordinateIndex = [6, 7, 4, -1, 10, 11, 8, -1, 14, 15, 12, -1]
        darkColorFaceset.coordIndex.setValues(
            0, len(darkColorCoordinateIndex), darkColorCoordinateIndex)

        lightNorthFaceset = coin.SoIndexedFaceSet()
        lightNorthCoordinateIndex = [2, 3, 0, -1]
        lightNorthFaceset.coordIndex.setValues(
            0, len(lightNorthCoordinateIndex), lightNorthCoordinateIndex)

        darkNorthFaceset = coin.SoIndexedFaceSet()
        darkNorthCoordinateIndex = [0, 1, 2, -1]
        darkNorthFaceset.coordIndex.setValues(
            0, len(darkNorthCoordinateIndex), darkNorthCoordinateIndex)

        self.compassswitch = coin.SoSwitch()
        self.compassswitch.whichChild = coin.SO_SWITCH_NONE
        self.compassswitch.addChild(compasssep)

        lightGreySeparator = coin.SoSeparator()
        lightGreySeparator.addChild(lightGreyMaterial)
        lightGreySeparator.addChild(lightColorFaceset)

        darkGreySeparator = coin.SoSeparator()
        darkGreySeparator.addChild(darkGreyMaterial)
        darkGreySeparator.addChild(darkColorFaceset)

        lightNorthSeparator = coin.SoSeparator()
        lightNorthSeparator.addChild(lightNorthMaterial)
        lightNorthSeparator.addChild(lightNorthFaceset)

        darkNorthSeparator = coin.SoSeparator()
        darkNorthSeparator.addChild(darkNorthMaterial)
        darkNorthSeparator.addChild(darkNorthFaceset)

        compasssep.addChild(coords)
        compasssep.addChild(self.transform)
        compasssep.addChild(lightGreySeparator)
        compasssep.addChild(darkGreySeparator)
        compasssep.addChild(lightNorthSeparator)
        compasssep.addChild(darkNorthSeparator)

        return self.compassswitch

    def buildCoordinates(self):
        from pivy import coin

        coords = coin.SoCoordinate3()

        # North Arrow
        coords.point.set1Value(0, 0, 0, 0)
        coords.point.set1Value(1, COMPASS_POINTER_WIDTH,
                               COMPASS_POINTER_WIDTH, 0)
        coords.point.set1Value(2, 0, COMPASS_POINTER_LENGTH, 0)
        coords.point.set1Value(3, -COMPASS_POINTER_WIDTH,
                               COMPASS_POINTER_WIDTH, 0)

        # East Arrow
        coords.point.set1Value(4, 0, 0, 0)
        coords.point.set1Value(
            5, COMPASS_POINTER_WIDTH, -COMPASS_POINTER_WIDTH, 0)
        coords.point.set1Value(6, COMPASS_POINTER_LENGTH, 0, 0)
        coords.point.set1Value(7, COMPASS_POINTER_WIDTH,
                               COMPASS_POINTER_WIDTH, 0)

        # South Arrow
        coords.point.set1Value(8, 0, 0, 0)
        coords.point.set1Value(
            9, -COMPASS_POINTER_WIDTH, -COMPASS_POINTER_WIDTH, 0)
        coords.point.set1Value(10, 0, -COMPASS_POINTER_LENGTH, 0)
        coords.point.set1Value(
            11, COMPASS_POINTER_WIDTH, -COMPASS_POINTER_WIDTH, 0)

        # West Arrow
        coords.point.set1Value(12, 0, 0, 0)
        coords.point.set1Value(13, -COMPASS_POINTER_WIDTH,
                               COMPASS_POINTER_WIDTH, 0)
        coords.point.set1Value(14, -COMPASS_POINTER_LENGTH, 0, 0)
        coords.point.set1Value(
            15, -COMPASS_POINTER_WIDTH, -COMPASS_POINTER_WIDTH, 0)

        return coords


class _PVPlantSite(ArchSite._Site):
    "The Site object"

    def __init__(self, obj):
        ArchSite._Site.__init__(self, obj)

        self.obj = obj
        # self.setProperties(obj)
        self.Type = "Site"
        obj.Proxy = self
        obj.IfcType = "Site"
        obj.setEditorMode("IfcType", 1)

    def setProperties(self, obj):
        # Definicion de Propiedades:
        ArchSite._Site.setProperties(self, obj)

        obj.addProperty("App::PropertyLink",
                        "Boundary",
                        "Site",
                        "Boundary of land")

        obj.addProperty("App::PropertyLinkList",
                        "Frames",
                        "Site",
                        "Frames templates")

        obj.addProperty("App::PropertyEnumeration",
                        "UtmZone",
                        "Base",
                        "UTM zone").UtmZone = zone_list

        obj.addProperty("App::PropertyVector",
                        "Origin",
                        "Base",
                        "Origin point.").Origin = (0, 0, 0)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored. Re-adds the properties."""
        self.obj = obj
        self.Type = "Site"
        obj.Proxy = self

    def onChanged(self, obj, prop):
        ArchSite._Site.onChanged(self, obj, prop)
        if (prop == "Terrain") or (prop == "Boundary"):
            if obj.Terrain and obj.Boundary:
                # TODO: Definir los objetos que se pueden proyectar
                # if obj.Boundary.TypeId == 'Part::Part2DObject':
                # projectWireOnMesh(obj.Boundary, obj.Terrain.Mesh)
                print("Calcular 3D boundary")

        if prop == "UtmZone":
            node = self.get_geoorigin()
            zone = obj.getPropertyByName("UtmZone")
            geo_system = ["UTM", zone, "FLAT"]
            node.geoSystem.setValues(geo_system)

        if prop == "Origin":
            node = self.get_geoorigin()
            origin = obj.getPropertyByName("Origin")
            node.geoCoords.setValue(origin.x, origin.y, 0)
            obj.Placement.Base = obj.getPropertyByName(prop)

    def execute(self, obj):

        return

        if not obj.isDerivedFrom("Part::Feature"):  # old-style Site
            return

        pl = obj.Placement
        shape = None
        if obj.Terrain:
            if obj.Terrain.isDerivedFrom("Part::Feature"):
                if obj.Terrain.Shape:
                    if not obj.Terrain.Shape.isNull():
                        shape = obj.Terrain.Shape.copy()
        if shape:
            shells = []
            for sub in obj.Subtractions:
                if sub.isDerivedFrom("Part::Feature"):
                    if sub.Shape:
                        if sub.Shape.Solids:
                            for sol in sub.Shape.Solids:
                                rest = shape.cut(sol)
                                shells.append(sol.Shells[0].common(shape.extrude(obj.ExtrusionVector)))
                                shape = rest
            for sub in obj.Additions:
                if sub.isDerivedFrom("Part::Feature"):
                    if sub.Shape:
                        if sub.Shape.Solids:
                            for sol in sub.Shape.Solids:
                                rest = shape.cut(sol)
                                shells.append(sol.Shells[0].cut(shape.extrude(obj.ExtrusionVector)))
                                shape = rest
            if not shape.isNull():
                if shape.isValid():
                    for shell in shells:
                        shape = shape.fuse(shell)
                    if obj.RemoveSplitter:
                        shape = shape.removeSplitter()
                    obj.Shape = shape
                    if not pl.isNull():
                        obj.Placement = pl
                    self.computeAreas(obj)

    def computeAreas(self, obj):
        ArchSite._Site.computeAreas(self, obj)
        return

        if not obj.Shape:
            return
        if obj.Shape.isNull():
            return
        if not obj.Shape.isValid():
            return
        if not obj.Shape.Faces:
            return
        if not hasattr(obj, "Perimeter"):  # check we have a latest version site
            return
        if not obj.Terrain:
            return
        # compute area
        fset = []
        for f in obj.Shape.Faces:
            if f.normalAt(0, 0).getAngle(FreeCAD.Vector(0, 0, 1)) < 1.5707:
                fset.append(f)
        if fset:
            import Drawing, Part
            pset = []
            for f in fset:
                try:
                    pf = Part.Face(Part.Wire(Drawing.project(f, FreeCAD.Vector(0, 0, 1))[0].Edges))
                except Part.OCCError:
                    # error in computing the area. Better set it to zero than show a wrong value
                    if obj.ProjectedArea.Value != 0:
                        print("Error computing areas for ", obj.Label)
                        obj.ProjectedArea = 0
                else:
                    pset.append(pf)
            if pset:
                self.flatarea = pset.pop()
                for f in pset:
                    self.flatarea = self.flatarea.fuse(f)
                self.flatarea = self.flatarea.removeSplitter()
                if obj.ProjectedArea.Value != self.flatarea.Area:
                    obj.ProjectedArea = self.flatarea.Area
        # compute perimeter
        lut = {}
        for e in obj.Shape.Edges:
            lut.setdefault(e.hashCode(), []).append(e)
        l = 0
        for e in lut.values():
            if len(e) == 1:  # keep only border edges
                l += e[0].Length
        if l:
            if obj.Perimeter.Value != l:
                obj.Perimeter = l
        # compute volumes
        if obj.Terrain.Shape.Solids:
            shapesolid = obj.Terrain.Shape.copy()
        else:
            shapesolid = obj.Terrain.Shape.extrude(obj.ExtrusionVector)
        addvol = 0
        subvol = 0
        for sub in obj.Subtractions:
            subvol += sub.Shape.common(shapesolid).Volume
        for sub in obj.Additions:
            addvol += sub.Shape.cut(shapesolid).Volume
        if obj.SubtractionVolume.Value != subvol:
            obj.SubtractionVolume = subvol
        if obj.AdditionVolume.Value != addvol:
            obj.AdditionVolume = addvol

    # Nuevo:
    def checkGeo(self):
        print(self.__getstate__())

    def __getstate__(self):
        """
        Save variables to file.
        """
        node = self.get_geoorigin()
        system = node.geoSystem.getValues()
        x, y, z = node.geoCoords.getValue().getValue()
        return system, [x, y, z]

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        print("State: ", state)
        if state:
            system = state[0]
            origin = state[1]
            node = self.get_geoorigin()

            node.geoSystem.setValues(system)
            node.geoCoords.setValue(origin[0], origin[1], 0)

    def get_geoorigin(self):
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        node = sg.getChild(0)

        if not isinstance(node, coin.SoGeoOrigin):
            node = coin.SoGeoOrigin()
            sg.insertChild(node, 0)
        return node

    def setLatLon(self, lat, lon):
        import utm
        x, y, zone_number, zone_letter = utm.from_latlon(lat, lon)
        self.obj.UtmZone = zone_list[zone_number - 1]
        # self.obj.UtmZone = "Z"+str(zone_number)
        self.obj.Origin = FreeCAD.Vector(x, y, 0.0) * 1000


class _ViewProviderSite(ArchSite._ViewProviderSite):
    """A View Provider for the Site object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a site view provider.
    """

    def __init__(self, vobj):
        ArchSite._ViewProviderSite.__init__(self, vobj)
        vobj.Proxy = self
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        self.setProperties(vobj)

    def getIcon(self):
        """
        Return the path to the appropriate icon.
        """
        return str(os.path.join(DirIcons, "solar-panel.svg"))

    def claimChildren(self):
        """Define which objects will appear as children in the tree view.

        Set objects within the site group, and the terrain object as children.

        If the Arch preference swallowSubtractions is true, set the additions
        and subtractions to the terrain as children.

        Returns
        -------
        list of <App::DocumentObject>s:
            The objects claimed as children.
        """

        objs = []
        if hasattr(self, "Object"):
            objs = self.Object.Group + \
                   [self.Object.Terrain, self.Object.Boundary, self.Object.Frames]
            if hasattr(self.Object, "Frames"):
                objs.extend(self.Object.Frames)

        return objs


'''
class _ViewProviderSite:
    """A View Provider for the Site object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a site view provider.
    """

    def __init__(self,vobj):
        vobj.Proxy = self
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        self.setProperties(vobj)

    def setProperties(self,vobj):
        """Give the site view provider its site view provider specific properties.

        These include solar diagram and compass data, dealing the orientation
        of the site, and its orientation to the sun.

        You can learn more about properties here: https://wiki.freecadweb.org/property
        """

        pl = vobj.PropertiesList
        if not "WindRose" in pl:
            vobj.addProperty("App::PropertyBool","WindRose","Site",QT_TRANSLATE_NOOP("App::Property","Show wind rose diagram or not. Uses solar diagram scale. Needs Ladybug module"))
        if not "SolarDiagram" in pl:
            vobj.addProperty("App::PropertyBool","SolarDiagram","Site",QT_TRANSLATE_NOOP("App::Property","Show solar diagram or not"))
        if not "SolarDiagramScale" in pl:
            vobj.addProperty("App::PropertyFloat","SolarDiagramScale","Site",QT_TRANSLATE_NOOP("App::Property","The scale of the solar diagram"))
            vobj.SolarDiagramScale = 1
        if not "SolarDiagramPosition" in pl:
            vobj.addProperty("App::PropertyVector","SolarDiagramPosition","Site",QT_TRANSLATE_NOOP("App::Property","The position of the solar diagram"))
        if not "SolarDiagramColor" in pl:
            vobj.addProperty("App::PropertyColor","SolarDiagramColor","Site",QT_TRANSLATE_NOOP("App::Property","The color of the solar diagram"))
            vobj.SolarDiagramColor = (0.16,0.16,0.25)
        if not "Orientation" in pl:
            vobj.addProperty("App::PropertyEnumeration", "Orientation", "Site", QT_TRANSLATE_NOOP(
                "App::Property", "When set to 'True North' the whole geometry will be rotated to match the true north of this site"))
            vobj.Orientation = ["Project North", "True North"]
            vobj.Orientation = "Project North"
        if not "Compass" in pl:
            vobj.addProperty("App::PropertyBool", "Compass", "Compass", QT_TRANSLATE_NOOP("App::Property", "Show compass or not"))
        if not "CompassRotation" in pl:
            vobj.addProperty("App::PropertyAngle", "CompassRotation", "Compass", QT_TRANSLATE_NOOP("App::Property", "The rotation of the Compass relative to the Site"))
        if not "CompassPosition" in pl:
            vobj.addProperty("App::PropertyVector", "CompassPosition", "Compass", QT_TRANSLATE_NOOP("App::Property", "The position of the Compass relative to the Site placement"))
        if not "UpdateDeclination" in pl:
            vobj.addProperty("App::PropertyBool", "UpdateDeclination", "Compass", QT_TRANSLATE_NOOP("App::Property", "Update the Declination value based on the compass rotation"))

    def onDocumentRestored(self,vobj):
        """Method run when the document is restored. Re-add the Arch component properties."""
        self.setProperties(vobj)

    def getIcon(self):
        """Return the path to the appropriate icon."""

        return str(os.path.join(DirIcons, "solar-panel.svg"))

    def claimChildren(self):
        """Define which objects will appear as children in the tree view.

        Set objects within the site group, and the terrain object as children.

        If the Arch preference swallowSubtractions is true, set the additions
        and subtractions to the terrain as children.

        Returns
        -------
        list of <App::DocumentObject>s:
            The objects claimed as children.
        """

        objs = []
        if hasattr(self,"Object"):
            objs = self.Object.Group+[self.Object.Terrain]
            prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
            if hasattr(self.Object,"Additions") and prefs.GetBool("swallowAdditions",True):
                objs.extend(self.Object.Additions)
            if hasattr(self.Object,"Subtractions") and prefs.GetBool("swallowSubtractions",True):
                objs.extend(self.Object.Subtractions)
        return objs

    def setEdit(self,vobj,mode):
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

        if (mode == 0) and hasattr(self,"Object"):
            import ArchComponent
            taskd = ArchComponent.ComponentTaskPanel()
            taskd.obj = self.Object
            taskd.update()
            FreeCADGui.Control.showDialog(taskd)
            return True
        return False

    def unsetEdit(self,vobj,mode):
        """Method called when the document requests the object exit edit mode.

        Close the Arch component edit task panel.

        Returns
        -------
        False
        """

        FreeCADGui.Control.closeDialog()
        return False

    def attach(self,vobj):
        """Add display modes' data to the coin scenegraph.

        Add each display mode as a coin node, whose parent is this view
        provider.

        Each display mode's node includes the data needed to display the object
        in that mode. This might include colors of faces, or the draw style of
        lines. This data is stored as additional coin nodes which are children
        of the display mode node.

        Doe not add display modes, but do add the solar diagram and compass to
        the scenegraph.
        """

        self.Object = vobj.Object
        from pivy import coin
        basesep = coin.SoSeparator()
        vobj.Annotation.addChild(basesep)
        self.color = coin.SoBaseColor()
        self.coords = coin.SoTransform()
        basesep.addChild(self.coords)
        basesep.addChild(self.color)
        self.diagramsep = coin.SoSeparator()
        self.diagramswitch = coin.SoSwitch()
        self.diagramswitch.whichChild = -1
        self.diagramswitch.addChild(self.diagramsep)
        basesep.addChild(self.diagramswitch)
        self.windrosesep = coin.SoSeparator()
        self.windroseswitch = coin.SoSwitch()
        self.windroseswitch.whichChild = -1
        self.windroseswitch.addChild(self.windrosesep)
        basesep.addChild(self.windroseswitch)
        self.compass = Compass()
        self.updateCompassVisibility(vobj)
        self.updateCompassScale(vobj)
        self.rotateCompass(vobj)
        vobj.Annotation.addChild(self.compass.rootNode)

    def updateData(self,obj,prop):
        """Method called when the host object has a property changed.

        If the Longitude or Latitude has changed, set the SolarDiagram to
        update.

        If Terrain or Placement has changed, move the compass to follow it.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The host object that has changed.
        prop: string
            The name of the property that has changed.
        """

        if prop in ["Longitude","Latitude"]:
            self.onChanged(obj.ViewObject,"SolarDiagram")
        elif prop == "Declination":
            self.onChanged(obj.ViewObject,"SolarDiagramPosition")
            self.updateTrueNorthRotation()
        elif prop == "Terrain":
            self.updateCompassLocation(obj.ViewObject)
        elif prop == "Placement":
            self.updateCompassLocation(obj.ViewObject)
            self.updateDeclination(obj.ViewObject)
        elif prop == "ProjectedArea":
            self.updateCompassScale(obj.ViewObject)

    def onChanged(self,vobj,prop):

        if prop == "SolarDiagramPosition":
            if hasattr(vobj,"SolarDiagramPosition"):
                p = vobj.SolarDiagramPosition
                self.coords.translation.setValue([p.x,p.y,p.z])
            if hasattr(vobj.Object,"Declination"):
                from pivy import coin
                self.coords.rotation.setValue(coin.SbVec3f((0,0,1)),math.radians(vobj.Object.Declination.Value))
        elif prop == "SolarDiagramColor":
            if hasattr(vobj,"SolarDiagramColor"):
                l = vobj.SolarDiagramColor
                self.color.rgb.setValue([l[0],l[1],l[2]])
        elif "SolarDiagram" in prop:
            if hasattr(self,"diagramnode"):
                self.diagramsep.removeChild(self.diagramnode)
                del self.diagramnode
            if hasattr(vobj,"SolarDiagram") and hasattr(vobj,"SolarDiagramScale"):
                if vobj.SolarDiagram:
                    tz = 0
                    if hasattr(vobj.Object,"TimeZone"):
                        tz = vobj.Object.TimeZone
                    self.diagramnode = makeSolarDiagram(vobj.Object.Longitude,vobj.Object.Latitude,vobj.SolarDiagramScale,tz=tz)
                    if self.diagramnode:
                        self.diagramsep.addChild(self.diagramnode)
                        self.diagramswitch.whichChild = 0
                    else:
                        del self.diagramnode
                else:
                    self.diagramswitch.whichChild = -1
        elif prop == "WindRose":
            if hasattr(self,"windrosenode"):
                del self.windrosenode
            if hasattr(vobj,"WindRose"):
                if vobj.WindRose:
                    if hasattr(vobj.Object,"EPWFile") and vobj.Object.EPWFile:
                        try:
                            import ladybug
                        except:
                            pass
                        else:
                            self.windrosenode = makeWindRose(vobj.Object.EPWFile,vobj.SolarDiagramScale)
                            if self.windrosenode:
                                self.windrosesep.addChild(self.windrosenode)
                                self.windroseswitch.whichChild = 0
                            else:
                                del self.windrosenode
                else:
                    self.windroseswitch.whichChild = -1
        elif prop == 'Visibility':
            if vobj.Visibility:
                self.updateCompassVisibility(self.Object)
            else:
                self.compass.hide()
        elif prop == 'Orientation':
            if vobj.Orientation == 'True North':
                self.addTrueNorthRotation()
            else:
                self.removeTrueNorthRotation()
        elif prop == "UpdateDeclination":
            self.updateDeclination(vobj)
        elif prop == "Compass":
            self.updateCompassVisibility(vobj)
        elif prop == "CompassRotation":
            self.updateDeclination(vobj)
            self.rotateCompass(vobj)
        elif prop == "CompassPosition":
            self.updateCompassLocation(vobj)

    def updateDeclination(self,vobj):
        """Update the declination of the compass

        Update the declination by adding together how the site has been rotated
        within the document, and the rotation of the site compass.
        """

        if not hasattr(vobj, 'UpdateDeclination') or not vobj.UpdateDeclination:
            return
        compassRotation = vobj.CompassRotation.Value
        siteRotation = math.degrees(vobj.Object.Placement.Rotation.Angle) # This assumes Rotation.axis = (0,0,1)
        vobj.Object.Declination = compassRotation + siteRotation

    def addTrueNorthRotation(self):

        if hasattr(self, 'trueNorthRotation') and self.trueNorthRotation is not None:
            return
        from pivy import coin
        self.trueNorthRotation = coin.SoTransform()
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        sg.insertChild(self.trueNorthRotation, 0)
        self.updateTrueNorthRotation()

    def removeTrueNorthRotation(self):

        if hasattr(self, 'trueNorthRotation') and self.trueNorthRotation is not None:
            sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
            sg.removeChild(self.trueNorthRotation)
            self.trueNorthRotation = None

    def updateTrueNorthRotation(self):

        if hasattr(self, 'trueNorthRotation') and self.trueNorthRotation is not None:
            from pivy import coin
            angle = self.Object.Declination.Value
            self.trueNorthRotation.rotation.setValue(coin.SbVec3f(0, 0, 1), math.radians(-angle))

    def updateCompassVisibility(self, vobj):

        if not hasattr(self, 'compass'):
            return
        show = hasattr(vobj, 'Compass') and vobj.Compass
        if show:
            self.compass.show()
        else:
            self.compass.hide()

    def rotateCompass(self, vobj):

        if not hasattr(self, 'compass'):
            return
        if hasattr(vobj, 'CompassRotation'):
            self.compass.rotate(vobj.CompassRotation.Value)

    def updateCompassLocation(self, vobj):

        if not hasattr(self, 'compass'):
            return
        if not vobj.Object.Shape:
            return
        boundBox = vobj.Object.Shape.BoundBox
        pos = vobj.Object.Placement.Base
        x = 0
        y = 0
        if hasattr(vobj, "CompassPosition"):
            x = vobj.CompassPosition.x
            y = vobj.CompassPosition.y
        z = boundBox.ZMax = pos.z
        self.compass.locate(x,y,z+1000)

    def updateCompassScale(self, vobj):

        if not hasattr(self, 'compass'):
            return
        self.compass.scale(vobj.Object.ProjectedArea)

    def __getstate__(self):

        return None

    def __setstate__(self,state):

        return None

'''


class _CommandPVPlantSite:
    "the Arch Site command definition"

    def GetResources(self):

        return {'Pixmap': str(os.path.join(DirIcons, "solar-panel.svg")),
                'MenuText': QT_TRANSLATE_NOOP("Arch_Site", "Site"),
                'Accel': "S, I",
                'ToolTip': QT_TRANSLATE_NOOP("Arch_Site", "Creates a site object including selected objects.")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        makePVPlantSite()
        return

        sel = FreeCADGui.Selection.getSelection()
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
        link = p.GetBool("FreeLinking", False)
        siteobj = []
        warning = False
        for obj in sel:
            if (Draft.getType(obj) == "Building") or (hasattr(obj, "IfcType") and obj.IfcType == "Building"):
                siteobj.append(obj)
            else:
                if link == True:
                    siteobj.append(obj)
                else:
                    warning = True
        if warning:
            message = translate("Arch", "Please either select only Building objects or nothing at all!\n\
Site is not allowed to accept any other object besides Building.\n\
Other objects will be removed from the selection.\n\
Note: You can change that in the preferences.")
            ArchCommands.printMessage(message)
        if sel and len(siteobj) == 0:
            message = translate("Arch", "There is no valid object in the selection.\n\
Site creation aborted.") + "\n"
            ArchCommands.printMessage(message)
        else:
            ss = "[ "
            for o in siteobj:
                ss += "FreeCAD.ActiveDocument." + o.Name + ", "
            ss += "]"
            FreeCAD.ActiveDocument.openTransaction(translate("Arch", "Create Site"))
            FreeCADGui.addModule("Arch")
            FreeCADGui.doCommand("obj = PVPlant.makePVPlantSite(" + ss + ")")
            FreeCADGui.addModule("Draft")
            FreeCADGui.doCommand("Draft.autogroup(obj)")
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantSite', _CommandPVPlantSite())
