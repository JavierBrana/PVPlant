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

import FreeCAD, Mesh, os, numpy, MeshPart, Arch, Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from PySide.QtCore import QT_TRANSLATE_NOOP
    from DraftTools import translate
else:
    def translate(ctxt, txt):
        return txt

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from PVPlantResources import DirIcons as DirIcons

## @package importDAE
#  \ingroup ARCH
#  \brief DAE (Collada) file format importer and exporter
#
#  This module provides tools to import and export Collada (.dae) files.

__title__ = "FreeCAD Collada importer"
__author__ = "Yorik van Havre"
__url__ = "http://www.freecadweb.org"

try:
    # Python 2 forward compatibility
    range = xrange
except NameError:
    pass


def checkCollada():
    "checks if collada if available"

    global collada
    COLLADA = None
    try:
        import collada
    except ImportError:
        FreeCAD.Console.PrintError(translate("Arch", "pycollada not found, collada support is disabled.") + "\n")
        return False
    else:
        return True


# from ARCH:
def triangulate(shape):
    "triangulates the given face"

    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
    mesher = p.GetInt("ColladaMesher", 0)
    tessellation = p.GetFloat("ColladaTessellation", 1.0)
    grading = p.GetFloat("ColladaGrading", 0.3)
    segsperedge = p.GetInt("ColladaSegsPerEdge", 1)
    segsperradius = p.GetInt("ColladaSegsPerRadius", 2)
    secondorder = p.GetBool("ColladaSecondOrder", False)
    optimize = p.GetBool("ColladaOptimize", True)
    allowquads = p.GetBool("ColladaAllowQuads", False)

    if mesher == 0:
        return shape.tessellate(tessellation)
    elif mesher == 1:
        return MeshPart.meshFromShape(Shape=shape, MaxLength=tessellation).Topology
    else:
        return MeshPart.meshFromShape(Shape=shape, GrowthRate=grading, SegPerEdge=segsperedge,
                                      SegPerRadius=segsperradius, SecondOrder=secondorder, Optimize=optimize,
                                      AllowQuad=allowquads).Topology

def export(exportList, filename, tessellation=1, colors=None):
    """export(exportList,filename,tessellation=1,colors=None) -- exports FreeCAD contents to a DAE file.
    colors is an optional dictionary of objName:shapeColorTuple or objName:diffuseColorList elements
    to be used in non-GUI mode if you want to be able to export colors. Tessellation is used when breaking
    curved surfaces into triangles."""

    if not checkCollada(): return

    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
    scale = p.GetFloat("ColladaScalingFactor", 1.0)
    scale = scale * 0.001  # from millimeters (FreeCAD) to meters (Collada)
    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
    c = p.GetUnsigned("DefaultShapeColor", 4294967295)
    defaultcolor = (float((c >> 24) & 0xFF) / 255.0, float((c >> 16) & 0xFF) / 255.0, float((c >> 8) & 0xFF) / 255.0)
    colmesh = collada.Collada()
    colmesh.assetInfo.upaxis = collada.asset.UP_AXIS.Z_UP

    # authoring info
    cont = collada.asset.Contributor()
    try:
        author = FreeCAD.ActiveDocument.CreatedBy
    except UnicodeEncodeError:
        author = FreeCAD.ActiveDocument.CreatedBy.encode("utf8")
    author = author.replace("<", "")
    author = author.replace(">", "")
    cont.author = author
    ver = FreeCAD.Version()
    appli = "PVPlant for FreeCAD" + ver[0] + "." + ver[1] + " build" + ver[2] + "\n"
    cont.authoring_tool = appli

    colmesh.assetInfo.contributors.append(cont)
    colmesh.assetInfo.unitname = "meter"
    colmesh.assetInfo.unitmeter = 1.0

    defaultmat = None
    objind = 0
    scenenodes = []

    # TODO: cambiar lo de objeclist. Buscar los elementos que se necesitan exportar
    objectlist = Draft.get_group_contents(exportList, walls=True, addgroups=True)
    objectlist = Arch.pruneIncluded(objectlist)
    for obj in objectlist:
        findex = numpy.array([])
        m = None
        if obj.isDerivedFrom("Part::Feature"):
            print("exporting object ", obj.Name, obj.Shape)
            new_shape = obj.Shape.copy()
            new_shape.Placement = obj.getGlobalPlacement()
            m = Mesh.Mesh(triangulate(new_shape))
        elif obj.isDerivedFrom("Mesh::Feature"):
            print("exporting object ", obj.Name, obj.Mesh)
            m = obj.Mesh
        elif obj.isDerivedFrom("App::Part"):
            for child in obj.OutList:
                objectlist.append(child)
            continue
        else:
            continue

        if m:
            Topology = m.Topology
            Facets = m.Facets

            # vertex indices
            vindex = numpy.empty(len(Topology[0]) * 3)
            for i in range(len(Topology[0])):
                v = Topology[0][i]
                vindex[list(range(i * 3, i * 3 + 3))] = (v.x * scale, v.y * scale, v.z * scale)

            # normals
            nindex = numpy.empty(len(Facets) * 3)
            for i in range(len(Facets)):
                n = Facets[i].Normal
                nindex[list(range(i * 3, i * 3 + 3))] = (n.x, n.y, n.z)

            # face indices
            findex = numpy.empty(len(Topology[1]) * 6, numpy.int64)
            for i in range(len(Topology[1])):
                f = Topology[1][i]
                findex[list(range(i * 6, i * 6 + 6))] = (f[0], i, f[1], i, f[2], i)

        print(len(vindex), " vert indices, ", len(nindex), " norm indices, ", len(findex), " face indices.")
        vert_src = collada.source.FloatSource("cubeverts-array" + str(objind), vindex, ('X', 'Y', 'Z'))
        normal_src = collada.source.FloatSource("cubenormals-array" + str(objind), nindex, ('X', 'Y', 'Z'))
        geom = collada.geometry.Geometry(colmesh, "geometry" + str(objind), obj.Name, [vert_src, normal_src])
        input_list = collada.source.InputList()
        input_list.addInput(0, 'VERTEX', "#cubeverts-array" + str(objind))
        input_list.addInput(1, 'NORMAL', "#cubenormals-array" + str(objind))
        matnode = None
        matref = "materialref"
        if hasattr(obj, "Material"):
            if obj.Material:
                if hasattr(obj.Material, "Material"):
                    if "DiffuseColor" in obj.Material.Material:
                        kd = tuple([float(k) for k in obj.Material.Material["DiffuseColor"].strip("()").split(",")])
                        effect = collada.material.Effect("effect_" + obj.Material.Name, [], "phong", diffuse=kd,
                                                         specular=(1, 1, 1))
                        mat = collada.material.Material("mat_" + obj.Material.Name, obj.Material.Name, effect)
                        colmesh.effects.append(effect)
                        colmesh.materials.append(mat)
                        matref = "ref_" + obj.Material.Name
                        matnode = collada.scene.MaterialNode(matref, mat, inputs=[])

        if not matnode:
            if colors:
                if obj.Name in colors:
                    color = colors[obj.Name]
                    if color:
                        if isinstance(color[0], tuple):
                            # this is a diffusecolor. For now, use the first color - #TODO: Support per-face colors
                            color = color[0]
                        # print("found color for obj",obj.Name,":",color)
                        kd = color[:3]
                        effect = collada.material.Effect("effect_" + obj.Name, [], "phong", diffuse=kd,
                                                         specular=(1, 1, 1))
                        mat = collada.material.Material("mat_" + obj.Name, obj.Name, effect)
                        colmesh.effects.append(effect)
                        colmesh.materials.append(mat)
                        matref = "ref_" + obj.Name
                        matnode = collada.scene.MaterialNode(matref, mat, inputs=[])
            elif FreeCAD.GuiUp:
                if hasattr(obj.ViewObject, "ShapeColor"):
                    kd = obj.ViewObject.ShapeColor[:3]
                    effect = collada.material.Effect("effect_" + obj.Name, [], "phong", diffuse=kd, specular=(1, 1, 1))
                    mat = collada.material.Material("mat_" + obj.Name, obj.Name, effect)
                    colmesh.effects.append(effect)
                    colmesh.materials.append(mat)
                    matref = "ref_" + obj.Name
                    matnode = collada.scene.MaterialNode(matref, mat, inputs=[])

        if not matnode:
            if not defaultmat:
                effect = collada.material.Effect("effect_default", [], "phong", diffuse=defaultcolor,
                                                 specular=(1, 1, 1))
                defaultmat = collada.material.Material("mat_default", "default_material", effect)
                colmesh.effects.append(effect)
                colmesh.materials.append(defaultmat)
            matnode = collada.scene.MaterialNode(matref, defaultmat, inputs=[])

        triset = geom.createTriangleSet(findex, input_list, matref)
        geom.primitives.append(triset)
        colmesh.geometries.append(geom)
        geomnode = collada.scene.GeometryNode(geom, [matnode])
        node = collada.scene.Node("node" + str(objind), children=[geomnode])
        scenenodes.append(node)
        objind += 1

    myscene = collada.scene.Scene("PVScene", scenenodes)
    colmesh.scenes.append(myscene)
    colmesh.scene = myscene
    colmesh.write(filename)

    FreeCAD.Console.PrintMessage(translate("Arch", "file %s successfully created.") % filename)

def exportToDAE(path):
    filename = path + ".dae"

def exportToPVC(path, exportTerrain = False):
    filename = path + ".pvc"

    import csv
    from xml.etree.ElementTree import Element, SubElement, Comment, tostring
    import datetime

    generated_on = str(datetime.datetime.now())
    exportList = FreeCAD.ActiveDocument.findObjects(Name="Tracker")
    exportList.pop(0)
    site = FreeCAD.ActiveDocument.getObjectsByLabel('Site')[0]
    terrain = site.Terrain.Mesh
    center = terrain.BoundBox.Center

    scale = 0.001  # from millimeters (FreeCAD) to meters (Collada)

    try:
        author = FreeCAD.ActiveDocument.CreatedBy
    except UnicodeEncodeError:
        author = FreeCAD.ActiveDocument.CreatedBy.encode("utf8")
    author = author.replace("<", "")
    author = author.replace(">", "")
    ver = FreeCAD.Version()
    appli = "PVPlant for FreeCAD" + ver[0] + "." + ver[1] + " build" + ver[2] + "\n"

    # xml: Configure one attribute with set()
    root = Element('COLLADA')
    root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('version', '1.4.1')
    root.set('xmlns', 'http://www.collada.org/2005/11/COLLADASchema')
    #root.append(Comment('Generated by ElementTree_csv_to_xml.py for PyMOTW'))

    # xml: 1. Asset:
    asset = SubElement(root, 'asset')
    asset_contributor = SubElement(asset, 'contributor')
    asset_contributor_autor = SubElement(asset_contributor, 'autor')
    #asset_contributor_autor.text = author
    asset_contributor_authoring_tool = SubElement(asset_contributor, 'authoring_tool')
    #asset_contributor_authoring_tool.text = appli
    asset_contributor_comments = SubElement(asset_contributor, 'comments')
    asset_keywords = SubElement(asset, 'keywords')
    asset_revision = SubElement(asset, 'revision')
    asset_subject = SubElement(asset, 'subject')
    asset_tittle = SubElement(asset, 'title')
    #asset_tittle.text = FreeCAD.ActiveDocument.Name
    asset_unit = SubElement(asset, 'unit')
    asset_unit.set('meter', '0.001')
    asset_unit.set('name', 'millimeter')

    # xml: 2. library_materials:
    library_materials = SubElement(root, 'library_materials')
    buf = ['Frames', 'Tree_trunk', 'Tree_crown', 'Topography_mesh']

    for i in range(0, len(buf)):
        material = SubElement(library_materials, 'material')
        material.set('id', 'Material{0}'.format(i))
        material.set('name', buf[i])
        material_effect = SubElement(material, 'instance_effect')
        material_effect.set('url', '#Material{0}-fx'.format(i))

    # xml: 3. library_effects:
    library_effects = SubElement(root, 'library_effects')
    buf = ['0.250000 0.500000 0.000000 1.000000',
           '0.500000 0.375000 0.250000 1.000000',
           '0.250000 1.000000 0.000000 1.000000',
           '0.250000 1.000000 0.000000 1.000000']

    for i in range(0, len(buf)):
        effect = SubElement(library_effects, 'effect')
        effect.set('id', 'Material{0}-fx'.format(i))
        effect.set('name', 'Material{0}'.format(i))
        profile_COMMON = SubElement(effect, 'profile_COMMON')
        library_effects_effect_technique = SubElement(profile_COMMON, 'technique')
        library_effects_effect_technique.set('sid', 'standard')
        library_effects_effect_technique_lambert = SubElement(library_effects_effect_technique, 'lambert')
        library_effects_effect_technique_lambert_emission = SubElement(library_effects_effect_technique_lambert,
                                                                       'emission')
        library_effects_effect_technique_lambert_emission_color = SubElement(
            library_effects_effect_technique_lambert_emission, 'color')
        library_effects_effect_technique_lambert_emission_color.set('sid', 'emission')
        library_effects_effect_technique_lambert_emission_color.text = '0.000000 0.000000 0.000000 1.000000'
        ambient = SubElement(library_effects_effect_technique_lambert, 'ambient')
        ambient_color = SubElement(ambient, 'color')
        ambient_color.set('sid', 'ambient')
        ambient_color.text = '0.200000 0.200000 0.200000 1.000000'
        diffuse = SubElement(library_effects_effect_technique_lambert, 'diffuse')
        diffuse_color = SubElement(diffuse, 'color')
        diffuse_color.set('sid', 'diffuse')
        diffuse_color.text = buf[i]
        transparent = SubElement(library_effects_effect_technique_lambert, 'transparent')
        transparent.set('opaque', 'RGB_ZERO')
        transparent_color = SubElement(transparent, 'color')
        transparent_color.set('sid', 'transparent')
        transparent_color.text = '0.000000 0.000000 0.000000 1.000000'
        transparency = SubElement(library_effects_effect_technique_lambert, 'transparency')
        transparency_value = SubElement(transparency, 'float')
        transparency_value.set('sid', 'transparency')
        transparency_value.text = '0'

    # xml: 4. library_geometries:
    library_geometries = SubElement(root, 'library_geometries')
    def add_geometry(objtype, vindex, findex, objind = 0, centers = None):
        isFrame = False
        if objtype == 0:
            geometryName = 'Frame'
            referenceSTR = 'frame'
            isFrame = True
        elif objtype == 1:
            geometryName = 'ShadowMesh'  ## --> ???
            referenceSTR = 'ShadowMesh'  ## --> ???
        elif objtype == 2:
            geometryName = 'TerrainMesh'
            referenceSTR = 'TerrainMesh'

        geometry = SubElement(library_geometries, 'geometry')
        geometry.set('id', geometryName + '{0}'.format(objind))
        mesh = SubElement(geometry, 'mesh')

        source = SubElement(mesh, 'source')
        source.set('id', referenceSTR + '{0}MeshSource'.format(objind))
        float_array = SubElement(source, 'float_array')
        float_array.set('id', referenceSTR + '{0}FloatArray'.format(objind))
        float_array.set('count', '{0}'.format(len(vindex)))
        float_array.text = ""  # vindex
        for ver in vindex:
            if len(float_array.text) > 0:
                float_array.text += ' '
            float_array.text += '{0:.6f}'.format(ver)

        technique_common = SubElement(source, 'technique_common')
        accessor = SubElement(technique_common, 'accessor')
        accessor.set('count', '{0}'.format(len(vindex)))
        accessor.set('source', '#' + referenceSTR + '{0}FloatArray'.format(objind))
        accessor.set('stride', '3')
        param = SubElement(accessor, 'param')
        param.set('name', 'X')
        param.set('type', 'float')
        param = SubElement(accessor, 'param')
        param.set('name', 'Y')
        param.set('type', 'float')
        param = SubElement(accessor, 'param')
        param.set('name', 'Z')
        param.set('type', 'float')

        vertices = SubElement(mesh, 'vertices')
        vertices.set('id', referenceSTR + '{0}VerticesSource'.format(objind))
        input = SubElement(vertices, "input")
        input.set('semantic', 'POSITION')
        input.set('source', '#' + referenceSTR + '{0}MeshSource'.format(objind))

        triangles = SubElement(mesh, 'triangles')
        triangles.set('count', '0')
        triangles.set('material', 'Material0')
        input = SubElement(triangles, "input")
        input.set('offset', '0')
        input.set('semantic', 'VERTEX')
        input.set('source', '#' + referenceSTR + '{0}VerticesSource'.format(objind))
        p = SubElement(triangles, "p")
        p.text = ''
        for f in findex:
            if len(p.text) > 0:
                p.text += ' '
            p.text += '{0}'.format(f)

        if isFrame:
            frame = SubElement(mesh, 'tracker_parameters' if isTracker else 'frame_parameters')
            module_width = SubElement(frame, "module_width")
            module_width.text = '{0}'.format(int(obj.ModuleWidth.Value))
            module_height = SubElement(frame, "module_height")
            module_height.text = '{0}'.format(int(obj.ModuleHeight.Value))
            module_x_spacing = SubElement(frame, "module_x_spacing")
            module_x_spacing.text = '{0}'.format(int(obj.ModuleColGap.Value))
            module_y_spacing = SubElement(frame, "module_y_spacing")
            module_y_spacing.text = '{0}'.format(int(obj.ModuleRowGap.Value))
            module_manufacturer = SubElement(frame, "module_manufacturer")
            module_manufacturer.text = 'generic'
            module_name = SubElement(frame, "module_name")
            module_name.text = 'generic'
            if isTracker:
                tracker_type = SubElement(frame, 'tracker_type')
                tracker_type.text = 'single_axis_trackers'
                axis = SubElement(frame, 'axis_vertices')
                for ind in range(0, len(centers)):
                    array = SubElement(axis, 'float_array')
                    array.set('id', 'tracker{0}AxisFloatArray1'.format(ind))
                    array.set('count', '3')
                    array.text = '{0:.6f} {1:.6f} {2:.6f}'.format(centers[i].x, centers[i].y, centers[i].z)

                min_phi = SubElement(frame, 'min_phi')
                min_phi.text = '{0}'.format(int(obj.MinPhi.Value))
                max_phi = SubElement(frame, 'max_phi')
                max_phi.text = '{0}'.format(int(obj.MaxPhi.Value))
                min_theta = SubElement(frame, 'min_theta')
                min_theta.text = '{0}'.format(0)
                max_theta = SubElement(frame, 'max_theta')
                max_theta.text = '{0}'.format(0)

        # xml: 5. library_visual_scenes:
        instance_geometry = SubElement(node, 'instance_geometry')
        instance_geometry.set('url', geometryName + '{0}'.format(objind))

        bind_material = SubElement(instance_geometry, 'bind_material')
        technique_common = SubElement(bind_material, 'technique_common')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material0')
        instance_material.set('target', '#Material0')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material1')
        instance_material.set('target', '#Material1')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material2')
        instance_material.set('target', '#Material2')

    # xml: 5. library_visual_scenes:
    library_visual_scenes = SubElement(root, 'library_visual_scenes')
    visual_scene = SubElement(library_visual_scenes, 'visual_scene')
    visual_scene.set('id', '')
    visual_scene.set('name', '')

    node = SubElement(visual_scene, 'node')
    node.set('id', 'Fbx_Root')
    node.set('name', 'Fbx_Root')
    node.set('sid', 'Fbx_Root')
    matrix = SubElement(node, 'matrix')
    matrix.set('sid', 'matrix')
    matrix.text = '1.000000 0.000000 0.000000 0.000000 0.000000 0.000000 -1.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 0.000000 0.000000 1.000000'
    node = SubElement(node, 'node')
    node.set('id', 'PVcase52')
    node.set('name', 'PVcase52')
    node.set('sid', 'PVcase52')
    matrix = SubElement(node, 'matrix')
    matrix.set('sid', 'matrix')
    matrix.text = '1.000000 0.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 0.000000 1.000000'

    extra = SubElement(visual_scene, 'extra')
    technique = SubElement(extra, 'technique')
    technique.set('profile', 'MAX3D')
    frame_rate = SubElement(technique, 'frame_rate')
    frame_rate.text = '30.000000'
    technique = SubElement(extra, 'technique')
    technique.set('profile', 'FCOLLADA')
    start_time = SubElement(technique, 'start_time')
    start_time.text = '0.000000'
    end_time = SubElement(technique, 'end_time')
    end_time.text = '1.000000'

    # xml: 6. scene:
    scene = SubElement(root, 'scene')
    instance = SubElement(scene, 'instance_visual_scene')
    instance.set('url', '#')

    # CASO 1 - FRAMES:
    frameType = site.Frames
    objind = 0
    for type in frameType:
        isTracker = "tracker" in type.Proxy.Type.lower()
        objectlist = FreeCAD.ActiveDocument.findObjects(Name="Tracker")

        for obj in objectlist:
            if obj.CloneOf == type:
                findex = numpy.array([])

                new_shape = obj.Shape.Faces[0].copy()
                new_shape.Placement = obj.Shape.Faces[0].Placement
                m = Mesh.Mesh(triangulate(new_shape))
                centers = []

                if isTracker:
                    minLengths = []
                    for ed in new_shape.Edges:
                        minLengths.append(ed.Length)
                    minLength = min(minLengths)
                    for ed in new_shape.Edges:
                        if ed.Length == minLength:
                            centers.append(ed.CenterOfMass)
                if m:
                    Topology = m.Topology

                    # vertex indices
                    vindex = numpy.empty(len(Topology[0]) * 3)
                    for i in range(len(Topology[0])):
                        v = Topology[0][i]
                        vindex[list(range(i * 3, i * 3 + 3))] = (-(v.x - center.x) * scale, (v.z - center.z) * scale,
                                                                 (v.y - center.y) * scale)

                    # face indices
                    findex = numpy.empty(len(Topology[1]) * 3, numpy.int64)
                    for i in range(len(Topology[1])):
                        f = Topology[1][i]
                        findex[list(range(i * 3, i * 3 + 3))] = (f[0], f[1], f[2])

                    add_geometry(0, vindex, findex, objind, centers if isTracker else None)
                    objind += 1

    # CASE 2: Shadow objects
    objectlist = FreeCAD.ActiveDocument.findObjects(Label = "Tree")  # TODO: Cambiar label por name
    objind = 0
    for obj in objectlist:
        findex = numpy.array([])
        m = None
        if obj.isDerivedFrom("Part::Feature"):
            new_shape = obj.Shape.copy()
            new_shape.Placement = obj.getGlobalPlacement()
            m = Mesh.Mesh(triangulate(new_shape))
        elif obj.isDerivedFrom("Mesh::Feature"):
            m = obj.Mesh
        elif obj.isDerivedFrom("App::Part"):
            for child in obj.OutList:
                objectlist.append(child)
            continue
        else:
            continue

        if m:
            Topology = m.Topology
            # vertex indices
            vindex = numpy.empty(len(Topology[0]) * 3)
            for i in range(len(Topology[0])):
                v = Topology[0][i]
                vindex[list(range(i * 3, i * 3 + 3))] = (-(v.x - center.x) * scale, (v.z - center.z) * scale,
                                                                 (v.y - center.y) * scale)

            # face indices
            findex = numpy.empty(len(Topology[1]) * 3, numpy.int64)
            for i in range(len(Topology[1])):
                f = Topology[1][i]
                findex[list(range(i * 3, i * 3 + 3))] = (f[0], f[1], f[2])

            add_geometry(1, vindex, findex, objind)
            objind += 1


    # CASE 3: Terrain
    # TODO: ver si se puede partir en varias mesh para que trabaje más rápido
    if exportTerrain:
        m = terrain
        if m:
            Topology = m.Topology
            # Facets = m.Facets

            # vertex indices
            vindex = numpy.empty(len(Topology[0]) * 3)
            for i in range(len(Topology[0])):
                v = Topology[0][i]
                vindex[list(range(i * 3, i * 3 + 3))] = (-v.x * scale, v.z * scale, v.y * scale)

            # face indices
            findex = numpy.empty(len(Topology[1]) * 3, numpy.int64)
            for i in range(len(Topology[1])):
                f = Topology[1][i]
                findex[list(range(i * 3, i * 3 + 3))] = (f[0], f[1], f[2])

            add_geometry(2, vindex, findex)

        # xml: 5. library_visual_scenes: ¿¿¿¿¿???????
        '''
        instance_geometry = SubElement(node, 'instance_geometry')
        instance_geometry.set('url', 'TerrainMesh{0}'.format(0))

        bind_material = SubElement(instance_geometry, 'bind_material')
        technique_common = SubElement(bind_material, 'technique_common')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material0')
        instance_material.set('target', '#Material0')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material1')
        instance_material.set('target', '#Material1')
        instance_material = SubElement(technique_common, 'instance_material')
        instance_material.set('symbol', 'Material2')
        instance_material.set('target', '#Material2')
        '''

    extra = SubElement(node, 'extra')
    technique = SubElement(extra, 'technique')
    technique.set('profile', 'FCOLLADA')
    visibility = SubElement(technique, 'visibility')
    visibility.text = '1.000000'


    # save the file:
    st = prettify(root)
    print(st)
    f = open(filename, "w")
    f.write(st)
    f.close()
    return True

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """

    from xml.etree import ElementTree
    from xml.dom import minidom

    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def exportToH2P(path):  # sólo válido para mesas
    filename = path + ".h2p"
    f2 = '{:.2f}'
    f3 = '{:.3f}'

    st = 'START\n'
    # TODO: hacer un bucle para cada tipo-tamaño de estructura.
    #       posible solucción: un primer bucle para identificar los tipos-tamaños de estructura
    #FreeCAD.ActiveDocument.findObjects
    #FreeCAD.ActiveDocument.Objects

    objects = FreeCAD.ActiveDocument.findObjects(Name="Tracker")
    grouptype = []
    #for obj in objects:
    grouptype.append(objects[0])

    for type in grouptype:
        st += 'TABLE\n' \
              '10\n'
        st += f3.format(type.Width.Value) + ',' + f3.format(type.Length.Value) + ','  + \
              f3.format(0)  + ',' + f3.format(0)  + ',' + f3.format(0)  + ',' + f3.format(0) + "\n"
              #'#{ f3 %pvsyst.ilb.to_mm },#{f3 %pvsyst.irb.to_mm},#{f3 %pvsyst.itb.to_mm},' \
              #'#{f3 %pvsyst.ibb.to_mm}\n'
        st += '20\n'
        st += str(int(type.ModulesCols.Value)) + ',' + str(int(type.ModulesRows.Value)) + ',' + \
              str(type.ModuleColGap.Value) + ',' + str(type.ModuleRowGap.Value) + ',' + '30\n'
        st += '30\n'
        st += '1,' + f3.format(type.ModuleWidth.Value) + ',' + f3.format(type.ModuleHeight.Value) + ',' + \
              f3.format(type.ModuleThick.Value) + ',' + f2.format(450) + '\n' #f2.format(type.ModulePower.Value) + '\n'

        # cornerdown = find_component_sizes(group.cdef)[1]
        # pvorigin = Geom::Point3d.new(cornerdown.x, cornerdown.y, 0)
        # group.instances.each{ | ins | str += pvsyst_insert(ins, pvorigin)}

        for obj in objects:
            if obj.CloneOf == type:
                st += H2PInsert(obj)

    ## TODO: Bucle para buscar objetos que den sombra y el terreno. Todos llaman a H2PMesh
    mesh = FreeCAD.ActiveDocument.getObjectsByLabel('Surface')[0].Mesh
    st += H2PMesh(mesh, False)
    st += "END\n"

    # save the file:
    f = open(filename, "w")
    f.write(st)
    f.close()

    return True

def H2PInsert(obj):
    import math

    f3 = '{:.3f}'
    f2 = '{:.2f}'
    scale = 0.001  ## ver como se puede hacer para que sea general. Pasar de mm a m

    st = 'INSERT\n' \
         '10\n'
    st += f3.format(obj.Placement.Base.x * scale) + ',' + f3.format(obj.Placement.Base.y * scale) + ',' + \
          f3.format((obj.Placement.Base.z + obj.PoleLength.Value - obj.RammingDeep.Value + 1000) * scale) + '\n'
    st += '50\n'
    st += f2.format(-obj.Placement.Rotation.toEuler()[0]) + '\n'
    st += '55\n'
    st += f2.format(obj.Placement.Rotation.toEuler()[1]) + '\n'
    st += '56\n'
    st += f2.format(obj.Placement.Rotation.toEuler()[2]) + '\n'

    return st

def H2PMesh(mesh, type):
    scale = 0.001  ## ver como se puede hacer para que sea general. Pasar de mm a m

    f3 = '{:.3f}'
    st = ''
    if type:
        st = 'ShadowObject\nFence\n'
    else:
        st = 'DGM\n'

    for face in mesh.Facets:
        p1 = face.Points[0]
        p2 = face.Points[1]
        p3 = face.Points[2]

        st += f3.format(p1[0] * scale) + "," + f3.format(p1[1] * scale) + "," + f3.format(p1[2] * scale) + ";"
        st += f3.format(p2[0] * scale) + "," + f3.format(p2[1] * scale) + "," + f3.format(p2[2] * scale) + ";"
        st += f3.format(p3[0] * scale) + "," + f3.format(p3[1] * scale) + "," + f3.format(p3[2] * scale) + "\n"

    return st

class _PVSystTaskPanel:

    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.dirname(__file__) + "/exportPVSyst.ui")
        self.form = self.form

    def show(self):
        # self.form.setWindowModality(Qt.WindowModal)
        self.form.show()

    def accept(self):
        path = os.path.dirname(FreeCAD.ActiveDocument.FileName)
        filename = os.path.join(path, FreeCAD.ActiveDocument.Name)

        #if self.form.cbDAE.isChecked():
        #    exportToDAE(filename)

        if self.form.cbPVC.isChecked():
            exportToPVC(filename, self.form.cbTerrain.isChecked())

        if self.form.cbH2P.isChecked():
            exportToH2P(filename)

        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCADGui.Control.closeDialog()
        return True

class _CommandExportToPVSyst:
    "Export to PVSyst"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "PVsyst.png")),
                'Accel': "E, P",
                'MenuText': QT_TRANSLATE_NOOP("Outputs", "Export to PVSyst"),
                'ToolTip': QT_TRANSLATE_NOOP("Outputs", "Exportar a PVSyst")}

    def Activated(self):
        taskd = _PVSystTaskPanel()
        # taskd.show()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('ExportToPVSyst', _CommandExportToPVSyst())
