'''
proctree.js
Copyright (c) 2012, Paul Brunt
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, self list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, self list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of tree.js nor the
      names of its contributors may be used to endorse or promote products
      derived from self software without specific prior written permission.

self SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL PAUL BRUNT BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES
LOSS OF USE, DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF self
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import math
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


def dot(self, v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def cross(self, v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

def length(self, v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def normalize(self, v):
    l = self.length(v)
    return self.scaleVec(v, 1 / l)

def scaleVec(self, v, s):
    return [v[0] * s, v[1] * s, v[2] * s]

def subVec(self, v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def addVec(self, v1, v2):
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

def vecAxisAngle(self, vec, axis, angle):
    # v cos(T) + (axis x v) * sin(T) + axis * (axis.v)(1 - cos(T)
    cosr = math.cos(angle)
    sinr = math.sin(angle)
    return self.addVec(self.addVec(self.scaleVec(vec, cosr),
                                   self.scaleVec(self.cross(axis, vec), sinr)),
                       self.scaleVec(axis, self.dot(axis, vec) * (1 - cosr)))

def scaleInDirection(self, vector, direction, scale):
    currentMag = self.dot(vector, direction)
    change = self.scaleVec(direction, currentMag * scale - currentMag)
    return self.addVec(vector, change)

def flattenArray(self, input):
    retArray = []
    for i in range(len(input)):
        for j in range(len(input[i])):
            retArray.push(input[i][j])
    return retArray




def makeTree(objectslist=None, baseobj=None, name="Tree"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Tree")
    _Tree(obj)
    _ViewProviderTree(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj

class Branch:

    def __init__(self, head, parent):
        self.head = head
        self.parent = parent
        self._child0 = None
        self._child1 = None
        self._length = 1

    def get_child0(self):
        return self._child0

    def set_child0(self, val):
        self._child0 = val

    def get_child1(self):
        return self._child1

    def set_child1(self, val):
        self._child1 = val

    def get_length(self):
        return self._length

    def set_length(self, val):
        self._length = val

    child0 = property(get_child0, set_child0)
    child1 = property(get_child1, set_child1)
    child1 = property(get_length, set_length)


    def mirrorBranch(self, vec, norm, properties):
        v = cross(norm, cross(vec, norm))
        s = properties.branchFactor * dot(v, vec)
        return [vec[0] - v[0] * s, vec[1] - v[1] * s, vec[2] - v[2] * s]

    def split(self, level, steps, properties, l1, l2):
        if l1 == None:
            l1 = 1
        if l2 == None:
            l2 = 1
        if level == None:
            level = properties.levels
        if steps == None:
            steps = properties.treeSteps

        rLevel = properties.levels - level
        po = None
        if (self.parent):
            po = self.parent.head
        else:
            po = [0, 0, 0]
            self.type = "trunk"

        so = self.head
        dir = normalize(subVec(so, po))
        normal = cross(dir, [dir[2], dir[0], dir[1]])
        tangent = cross(dir, normal)
        r = properties.random(rLevel * 10 + l1 * 5 + l2 + properties.seed)
        r2 = properties.random(rLevel * 10 + l1 * 5 + l2 + 1 + properties.seed)
        clumpmax = properties.clumpMax
        clumpmin = properties.clumpMin
        adj = addVec(scaleVec(normal, r), scaleVec(tangent, 1 - r))
        if (r > 0.5):
            adj = scaleVec(adj, -1)

        clump = (clumpmax - clumpmin) * r + clumpmin
        newdir = normalize(addVec(scaleVec(adj, 1 - clump), scaleVec(dir, clump)))
        newdir2 = self.mirrorBranch(newdir, dir, properties)

        if (r > 0.5):
            tmp = newdir
            newdir = newdir2
            newdir2 = tmp

        if (steps > 0):
            angle = steps / properties.treeSteps * 2 * math.pi * properties.twistRate
            newdir2 = normalize([Math.sin(angle), r, math.cos(angle)])

        growAmount = level * level / (properties.levels * properties.levels) * properties.growAmount
        dropAmount = rLevel * properties.dropAmount
        sweepAmount = rLevel * properties.sweepAmount
        newdir = normalize(addVec(newdir, [sweepAmount, dropAmount + growAmount, 0]))
        newdir2 = normalize(addVec(newdir2, [sweepAmount, dropAmount + growAmount, 0]))
        head0 = addVec(so, scaleVec(newdir, length))
        head1 = addVec(so, scaleVec(newdir2, length))
        self.child0 = Branch(head0, self)
        self.child1 = Branch(head1, self)
        self.child0.length = math.pow(length, properties.lengthFalloffPower) * properties.lengthFalloffFactor
        self.child1.length = math.pow(length, properties.lengthFalloffPower) * properties.lengthFalloffFactor
        if (level > 0):
            if (steps > 0):
                self.child0.head = addVec(self.head, [(r - 0.5) * 2 * properties.trunkKink, properties.climbRate,
                                                      (r - 0.5) * 2 * properties.trunkKink])
                self.child0.type = "trunk"
                self.child0.length = length * properties.taperRate
                self.child0.split(level, steps - 1, properties, l1 + 1, l2)
            else:
                self.child0.split(level - 1, 0, properties, l1 + 1, l2)
            self.child1.split(level - 1, 0, properties, l1, l2 + 1)



class _Tree(ArchComponent.Component):
    "A Shadow Tree Obcject"

    def __init__(self, obj):
        # TODO: si el obj = none crear un objeto. Caso contrario editarlo.
        self.obj = obj

        # Definición de  variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        # Does a IfcType exist?
        obj.IfcType = "Shading Device"
        # obj.MoveWithHost = False


        # ESto son propiedades. Mover y convertir a propiedades
        self.clumpMax = 0.8
        self.clumpMin = 0.5
        self.lengthFalloffFactor = 0.85
        self.lengthFalloffPower = 1
        self.branchFactor = 2.0
        self.radiusFalloffRate = 0.6
        self.climbRate = 1.5
        self.trunkKink = 0.00
        self.maxRadius = 0.25
        self.treeSteps = 2
        self.taperRate = 0.95
        self.twistRate = 13
        self.segments = 6
        self.levels = 3
        self.sweepAmount = 0
        self.initalBranchLength = 0.85
        self.trunkLength = 2.5
        self.dropAmount = 0.0
        self.growAmount = 0.0
        self.vMultiplier = 0.2
        self.twigScale = 2.0
        self.seed = 10
        self.rseed = 10

        '''
        for i in data:
            if self.properties[i] != None:
                self.properties[i] = data[i]
        '''

        self.rseed = self.seed

        self.root = Branch([0, self.trunkLength, 0], self)
        self.root.length = self.initalBranchLength
        self.verts = []
        self.faces = []
        self.normals = []
        self.UV = []
        self.vertsTwig = []
        self.normalsTwig = []
        self.facesTwig = []
        self.uvsTwig = []
        self.root.split(None, None, self.properties)
        self.createForks()
        self.createTwigs()
        self.doFaces()
        self.calcNormals()


    def random(self, a):
        if not a:
            a = self.rseed + 1
        return math.abs(math.cos(a + a * a))

    def setProperties(self, obj):
        # Definicion de Propiedades:
        ArchComponent.Component.setProperties(self, obj)

        # CANOPY: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "CanopyHeight",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).CanopyHeight = 4000

        obj.addProperty("App::PropertyLength",
                        "CanopyRadius",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).CanopyRadius = 1500

        obj.addProperty("App::PropertyFloat",
                        "Spikiness",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Spikiness = 0.15

        obj.addProperty("App::PropertyFloat",
                        "Lumpiness",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Lumpiness = 0.15

        obj.addProperty("App::PropertyFloat",
                        "Crown",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).Crown = 1.0

        obj.addProperty("App::PropertyQuantity",
                        "LeafCount",
                        "Canopy",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).LeafCount = 64

        # TRUNK: ------------------------------------------------------------------------------------------------------
        obj.addProperty("App::PropertyLength",
                        "TrunkHeight",
                        "Trunk",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).TrunkHeight = 1122

        obj.addProperty("App::PropertyLength",
                        "TrunkRadius",
                        "Trunk",
                        QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                        ).TrunkRadius = 147

        obj.addProperty("App::PropertyQuantity",
                       "TrunkFaces",
                       "Trunk",
                       QT_TRANSLATE_NOOP("App::Property", "The height of self object")
                       ).TrunkFaces = 6

        obj.setEditorMode("TrunkFaces", 1)

        self.Type = "Fixed Rack"
        obj.Proxy = self

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
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def calcNormals(self):
        normals = self.normals
        faces = self.faces
        verts = self.verts
        allNormals = []

        for i in range(len(verts)):
            allNormals[i] = []

        for i in range(len(faces)):
            face = faces[i]
            norm = normalize(self.cross(subVec(verts[face[1]], verts[face[2]]), subVec(verts[face[1]], verts[face[0]])))
            allNormals[face[0]].append(norm)
            allNormals[face[1]].append(norm)
            allNormals[face[2]].append(norm)

        for i in range(len(allNormals)):
            total = [0, 0, 0]
            l = len(allNormals[i])
            for j in range(l):
                total = addVec(total, scaleVec(allNormals[i][j], 1 / l))
            normals[i] = total

    def doFaces(self, branch):
        if not branch:
            branch = self.root

        segments = self.properties.segments
        faces = self.faces
        verts = self.verts

        UV = self.UV
        if not branch.parent:
            for i in len(verts):
                UV[i] = [0, 0]

            tangent = normalize(self.cross(subVec(branch.child0.head, branch.head), subVec(branch.child1.head, branch.head)))
            normal = normalize(branch.head)
            angle = math.acos(self.dot(tangent, [-1, 0, 0]))

            if self.dot(self.cross([-1, 0, 0], tangent), normal) > 0:
                angle = 2 * math.pi - angle
            segOffset = round((angle / math.PI / 2 * segments))

            for i in segments:
                v1 = branch.ring0[i]
                v2 = branch.root[(i + segOffset + 1) % segments]
                v3 = branch.root[(i + segOffset) % segments]
                v4 = branch.ring0[(i + 1) % segments]

                faces.append([v1, v4, v3])
                faces.append([v4, v2, v3])
                UV[(i + segOffset) % segments] = [abs(i / segments - 0.5) * 2, 0]
                lng = self.length(subVec(verts[branch.ring0[i]], verts[branch.root[(i + segOffset) % segments]])) * self.vMultiplier
                UV[branch.ring0[i]] = [abs(i / segments - 0.5) * 2, lng]
                UV[branch.ring2[i]] = [abs(i / segments - 0.5) * 2, lng]

            if branch.child0.ring0:
                segOffset0 = None
                segOffset1 = None
                match0 = None
                match1 = None

                v1 = normalize(subVec(verts[branch.ring1[0]], branch.head))
                v2 = normalize(subVec(verts[branch.ring2[0]], branch.head))

                v1 = scaleInDirection(v1, normalize(subVec(branch.child0.head, branch.head)), 0)
                v2 = scaleInDirection(v2, normalize(subVec(branch.child1.head, branch.head)), 0)

                for i in segments:
                    d = normalize(subVec(verts[branch.child0.ring0[i]], branch.child0.head))
                    l = self.dot(d, v1)
                    if (segOffset0 == None) or (l > match0):
                        match0 = l
                        segOffset0 = segments - i

                    d = normalize(subVec(verts[branch.child1.ring0[i]], branch.child1.head))
                    l = self.dot(d, v2)
                    if (segOffset1 == None) or (l > match1):
                        match1 = l
                        segOffset1 = segments - i

                UVScale = self.properties.maxRadius / branch.radius

                for i in segments:
                    v1 = branch.child0.ring0[i]
                    v2 = branch.ring1[(i + segOffset0 + 1) % segments]
                    v3 = branch.ring1[(i + segOffset0) % segments]
                    v4 = branch.child0.ring0[(i + 1) % segments]
                    faces.append([v1, v4, v3])
                    faces.append([v4, v2, v3])
                    v1 = branch.child1.ring0[i]
                    v2 = branch.ring2[(i + segOffset1 + 1) % segments]
                    v3 = branch.ring2[(i + segOffset1) % segments]
                    v4 = branch.child1.ring0[(i + 1) % segments]
                    faces.append([v1, v2, v3])
                    faces.append([v1, v4, v2])

                    len1 = self.length(subVec(verts[branch.child0.ring0[i]], verts[branch.ring1[(i + segOffset0) % segments]])) * UVScale
                    uv1 = UV[branch.ring1[(i + segOffset0 - 1) % segments]]

                    UV[branch.child0.ring0[i]] = [uv1[0], uv1[1] + len1 * self.properties.vMultiplier]
                    UV[branch.child0.ring2[i]] = [uv1[0], uv1[1] + len1 * self.properties.vMultiplier]

                    len2 = self.length(subVec(verts[branch.child1.ring0[i]], verts[branch.ring2[(i + segOffset1) % segments]])) * UVScale
                    uv2 = UV[branch.ring2[(i + segOffset1 - 1) % segments]]

                    UV[branch.child1.ring0[i]] = [uv2[0], uv2[1] + len2 * self.properties.vMultiplier]
                    UV[branch.child1.ring2[i]] = [uv2[0], uv2[1] + len2 * self.properties.vMultiplier]

                self.doFaces(branch.child0)
                self.doFaces(branch.child1)

            else:
                for i in segments:
                    faces.append([branch.child0.end, branch.ring1[(i + 1) % segments], branch.ring1[i]])
                    faces.append([branch.child1.end, branch.ring2[(i + 1) % segments], branch.ring2[i]])

                    ln = self.length(subVec(verts[branch.child0.end], verts[branch.ring1[i]]))
                    UV[branch.child0.end] = [math.abs(i / segments - 1 - 0.5) * 2, ln * self.properties.vMultiplier]
                    len = self.length(subVec(verts[branch.child1.end], verts[branch.ring2[i]]))
                    UV[branch.child1.end] = [math.abs(i / segments - 0.5) * 2, len * self.properties.vMultiplier]

    def createTwigs(self, branch = None):

        if branch is None: branch = self.root
        vertsTwig = self.vertsTwig
        normalsTwig = self.normalsTwig
        facesTwig = self.facesTwig
        uvsTwig = self.uvsTwig

        if not branch.child0:
            tangent = normalize(cross(subVec(branch.parent.child0.head, branch.parent.head),
                                      subVec(branch.parent.child1.head, branch.parent.head)))
            binormal = normalize(subVec(branch.head, branch.parent.head))
            normal = cross(tangent, binormal)

            vert1 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, self.properties.twigScale)),
                                  scaleVec(binormal, self.properties.twigScale * 2 - branch.length)))
            vert2 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, -self.properties.twigScale)),
                                  scaleVec(binormal, self.properties.twigScale * 2 - branch.length)))
            vert3 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, -self.properties.twigScale)),
                                  scaleVec(binormal, -branch.length)))
            vert4 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, self.properties.twigScale)),
                                  scaleVec(binormal, -branch.length)))

            vert8 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, self.properties.twigScale)),
                                  scaleVec(binormal, self.properties.twigScale * 2 - branch.length)))
            vert7 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, -self.properties.twigScale)),
                                  scaleVec(binormal, self.properties.twigScale * 2 - branch.length)))
            vert6 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, -self.properties.twigScale)),
                                  scaleVec(binormal, -branch.length)))
            vert5 = vertsTwig.length
            vertsTwig.push(addVec(addVec(branch.head, scaleVec(tangent, self.properties.twigScale)),
                                  scaleVec(binormal, -branch.length)))

            facesTwig.push([vert1, vert2, vert3])
            facesTwig.push([vert4, vert1, vert3])

            facesTwig.push([vert6, vert7, vert8])
            facesTwig.push([vert6, vert8, vert5])

            normal = normalize(
                self.cross(subVec(vertsTwig[vert1], vertsTwig[vert3]), subVec(vertsTwig[vert2], vertsTwig[vert3])))
            normal2 = normalize(
                self.cross(subVec(vertsTwig[vert7], vertsTwig[vert6]), subVec(vertsTwig[vert8], vertsTwig[vert6])))

            normalsTwig.push(normal)
            normalsTwig.push(normal)
            normalsTwig.push(normal)
            normalsTwig.push(normal)

            normalsTwig.push(normal2)
            normalsTwig.push(normal2)
            normalsTwig.push(normal2)
            normalsTwig.push(normal2)

            uvsTwig.push([0, 1])
            uvsTwig.push([1, 1])
            uvsTwig.push([1, 0])
            uvsTwig.push([0, 0])

            uvsTwig.push([0, 1])
            uvsTwig.push([1, 1])
            uvsTwig.push([1, 0])
            uvsTwig.push([0, 0])

        else:
            self.createTwigs(branch.child0)
            self.createTwigs(branch.child1)

    def createForks(self, branch=None, radius=None):
        if branch is None:
            branch = self.root
        if radius is None:
            radius = self.maxRadius

        branch.radius = radius

        if radius > branch.length:
            radius = branch.length

        verts = self.verts
        segments = self.segments
        segmentAngle = math.pi * 2 / segments

        if not branch.parent:
            # create the root of the tree
            branch.root = []
            axis = [0, 1, 0]
            for i in range(segments):
                vec = vecAxisAngle([-1, 0, 0], axis, -segmentAngle * i)
                branch.root.push(verts.length)
                verts.push(scaleVec(vec, radius / self.properties.radiusFalloffRate))

        # cross the branches to get the left
        # add the branches to get the up
        if branch.child0:
            if branch.parent:
                axis = normalize(subVec(branch.head, branch.parent.head))
            else:
                axis = normalize(branch.head)

            axis1 = normalize(subVec(branch.head, branch.child0.head))
            axis2 = normalize(subVec(branch.head, branch.child1.head))
            tangent = normalize(self.cross(axis1, axis2))
            branch.tangent = tangent

            axis3 = normalize(self.cross(tangent, normalize(addVec(scaleVec(axis1, -1), scaleVec(axis2, -1)))))
            dir = [axis2[0], 0, axis2[2]]
            centerloc = addVec(branch.head, scaleVec(dir, -self.properties.maxRadius / 2))

            ring0 = branch.ring0 = []
            ring1 = branch.ring1 = []
            ring2 = branch.ring2 = []

            scale = self.properties.radiusFalloffRate

            if (branch.child0.type == "trunk") or (branch.type == "trunk"):
                scale = 1 / self.properties.taperRate

            # main segment ring
            linch0 = len(verts)
            ring0.push(linch0)
            ring2.push(linch0)
            verts.push(addVec(centerloc, scaleVec(tangent, radius * scale)))

            start = len(verts) - 1
            d1 = vecAxisAngle(tangent, axis2, 1.57)
            d2 = normalize(self.cross(tangent, axis))
            s = 1 / self.dot(d1, d2)
            for i in range(1, segments / 2):
                vec = vecAxisAngle(tangent, axis2, segmentAngle * i)
                ring0.push(start + i)
                ring2.push(start + i)
                vec = scaleInDirection(vec, d2, s)
                verts.push(addVec(centerloc, scaleVec(vec, radius * scale)))

            linch1 = verts.length
            ring0.push(linch1)
            ring1.push(linch1)
            verts.push(addVec(centerloc, scaleVec(tangent, -radius * scale)))
            for i in range(segments / 2 + 1, segments):
                vec=vecAxisAngle(tangent, axis1, segmentAngle * i)
                ring0.push(verts.length)
                ring1.push(verts.length)
                verts.push(addVec(centerloc, scaleVec(vec, radius * scale)))

            ring1.push(linch0)
            ring2.push(linch1)
            start=verts.length-1
            for i in range(1, segments / 2):
                vec=vecAxisAngle(tangent, axis3, segmentAngle * i)
                ring1.push(start+i)
                ring2.push(start+(segments / 2-i))
                v=scaleVec(vec, radius * scale)
                verts.push(addVec(centerloc, v))


            # child radius is related to the brans direction and the length of the branch
            length0 = self.length(subVec(branch.head, branch.child0.head))
            length1 = self.length(subVec(branch.head, branch.child1.head))

            radius0=1 * radius * self.properties.radiusFalloffRate
            radius1=1 * radius * self.properties.radiusFalloffRate
            if (branch.child0.type == "trunk"):
                radius0=radius * self.properties.taperRate
            self.createForks(branch.child0, radius0)
            self.createForks(branch.child1, radius1)
        else:
            # add points for the ends of braches
            branch.end = len(verts)
            # branch.head=addVec(branch.head, scaleVec([self.properties.xBias, self.properties.yBias, self.properties.zBias], branch.length * 3))
            verts.append(branch.head)

    def execute(self, obj):
        print("  -----  TREE  -  EXECUTE  ----------")
        from datetime import datetime
        starttime = datetime.now()

        pl = obj.Placement
            ## aquí el código ------------------------------


        obj.Placement = pl


        print("  --  Tree done: (", datetime.now() - starttime, ")")


class _ViewProviderTree(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "tree(1).svg"))


class _TreeTaskPanel:

    def __init__(self, obj=None):
        self.obj = obj

        self.formRack = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")
        self.formRack.widgetTracker.setVisible(False)
        self.formRack.comboFrameType.currentIndexChanged.connect(self.selectionchange)

        self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")
        self.form = [self.formRack, self.formPiling]

        # signals/slots
        # QtCore.QObject.connect(self.valueModuleLength,QtCore.SIGNAL("valueChanged(double)"),self.setModuleLength)
        # QtCore.QObject.connect(self.valueModuleWidth,QtCore.SIGNAL("valueChanged(double)"),self.setModuleWidth)
        # QtCore.QObject.connect(self.valueModuleHeight,QtCore.SIGNAL("valueChanged(double)"),self.setModuleHeight)
        # QtCore.QObject.connect(self.valueModuleFrame, QtCore.SIGNAL("valueChanged(double)"), self.setModuleFrame)
        # QtCore.QObject.connect(self.valueModuleColor, QtCore.SIGNAL("valueChanged(double)"), self.setModuleColor)
        # QtCore.QObject.connect(self.valueModuleGapX, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapX)
        # QtCore.QObject.connect(self.valueModuleGapY, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapY)

    def selectionchange(self, i):
        vis = False
        if i == 1:
            vis = True

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


class _CommandTree:
    "the PVPlant Tree command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "tree(1).svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTree", "Tree"),
                'Accel': "S, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTree",
                                                    "Creates a Tree object from setup dialog.")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        print("_CommandTracker - Activated")
        obj = makeTree()
        self.TreePanel = _TreeTaskPanel()
        #FreeCADGui.Control.showDialog(self.TreePanel)
        FreeCADGui.Snapper.getPoint(callback = self.getPoint,
                                    extradlg = self.taskbox(),
                                    title=translate("PVPlant", "Position of the tree") + ":")

    def taskbox(self):
        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantTree.ui")
        #self.formPiling = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRackFixedPiling.ui")

        return self.form  #, self.formPiling]


    def getPoint(self, point=None, obj=None):
        """Callback for clicks

        Parameters
        ----------
        point: <class 'Base.Vector'>
            The point the user has selected.
        obj: <Part::PartFeature>, optional
            The object the user's cursor snapped to, if any.
        """

        '''
        if obj:
            if Draft.getType(obj) == "Wall":
                if not obj in self.existing:
                    self.existing.append(obj)
        if point is None:
            self.tracker.finalize()
            return
        self.points.append(point)
        '''
        '''
        if len(self.points) == 1:
            self.tracker.width(self.Width)
            self.tracker.height(self.Height)
            self.tracker.on()
            FreeCADGui.Snapper.getPoint(last=self.points[0],
                                        callback=self.getPoint,
                                        movecallback=self.update,
                                        extradlg=self.taskbox(),
                                        title=translate("Arch", "Next point") + ":", mode="line")

        elif len(self.points) == 2:
            import Part
            l = Part.LineSegment(FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[0]),
                                 FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[1]))
            self.tracker.finalize()
            FreeCAD.ActiveDocument.openTransaction(translate("Arch", "Create Wall"))
            FreeCADGui.addModule("Arch")
            FreeCADGui.doCommand('import Part')
            FreeCADGui.doCommand(
                'trace=Part.LineSegment(FreeCAD.' + str(l.StartPoint) + ',FreeCAD.' + str(l.EndPoint) + ')')
            if not self.existing:
                # no existing wall snapped, just add a default wall
                self.addDefault()
            else:
                if self.JOIN_WALLS_SKETCHES:
                    # join existing subwalls first if possible, then add the new one
                    w = joinWalls(self.existing)
                    if w:
                        if areSameWallTypes([w, self]):
                            FreeCADGui.doCommand('FreeCAD.ActiveDocument.' + w.Name + '.Base.addGeometry(trace)')
                        else:
                            # if not possible, add new wall as addition to the existing one
                            self.addDefault()
                            if self.AUTOJOIN:
                                FreeCADGui.doCommand(
                                    'Arch.addComponents(FreeCAD.ActiveDocument.' + FreeCAD.ActiveDocument.Objects[
                                        -1].Name + ',FreeCAD.ActiveDocument.' + w.Name + ')')
                    else:
                        self.addDefault()
                else:
                    # add new wall as addition to the first existing one
                    self.addDefault()
                    if self.AUTOJOIN:
                        FreeCADGui.doCommand(
                            'Arch.addComponents(FreeCAD.ActiveDocument.' + FreeCAD.ActiveDocument.Objects[
                                -1].Name + ',FreeCAD.ActiveDocument.' + self.existing[0].Name + ')')
        '''


        print("-------  Get point to generate new tree ------------------------------------")
        print(point, " - ", obj)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()
        #if self.continueCmd:
        self.Activated()


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantTree', _CommandTree())