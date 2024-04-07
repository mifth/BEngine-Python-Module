import bpy
import bmesh

# import mathutils

import numpy as np

from .. import BESettings
from ..BESettings import EngineType


def CreateEmptyMesh():
    empty_mesh_data = bpy.data.meshes.new('BESubMesh')

    # For Blender 4.0-
    if bpy.app.version[0] < 4 or (bpy.app.version[0] == 4 and bpy.app.version[1] == 0):
        empty_mesh_data.use_auto_smooth = True

    return empty_mesh_data


# Create Mesh
def CreateMesh(polys_len, np_verts, np_poly_indices, np_normals):
    mesh = bpy.data.meshes.new('BESubMesh')

    mesh.vertices.add(int(len(np_verts) / 3))
    mesh.vertices.foreach_set('co', np_verts)

    mesh.polygons.add(polys_len)

    mesh.loops.add(len(np_poly_indices))
    mesh.loops.foreach_set("vertex_index", np_poly_indices)

    np_loop_start = np.arange(0, (polys_len * 3) - 1, 3, dtype=np.int32)
    mesh.polygons.foreach_set('loop_start', np_loop_start)

    np_loops_total = np.full(polys_len, 3, dtype=np.int32)
    mesh.polygons.foreach_set('loop_total', np_loops_total)

    # Smooth
    np_smooth = np.full(polys_len, 1, dtype=np.int8)
    mesh.polygons.foreach_set("use_smooth", np_smooth)

    # For Blender 4.0-
    if bpy.app.version[0] < 4 or (bpy.app.version[0] == 4 and bpy.app.version[1] == 0):
        mesh.use_auto_smooth = True

    # be_sub_mesh.validate()
    mesh.update()

    # Normals
    if np_normals is not None and len(np_normals) > 0:
        mesh.normals_split_custom_set_from_vertices(np_normals)
    # normals2 = [js_mesh["Normals"][loop.vertex_index] for loop in be_sub_mesh.loops]
    # be_sub_mesh.normals_split_custom_set(normals2)

    return mesh


def MeshFromJSON(js_mesh, engine_type: EngineType):

    if "Verts" in js_mesh and js_mesh["Verts"]:
        # np_verts = np.asarray(js_mesh["Verts"], dtype=np.float32)
        np_verts = js_mesh["Verts"]

        # np_poly_indices = np.asarray(js_mesh["PolyIndices"], dtype=np.int32)
        np_poly_indices = js_mesh["PolyIndices"]

        polys_len = int(len(js_mesh["PolyIndices"]) / 3)  # Triangles Only

        np_normals = None
        if "Normals" in js_mesh:
            np_normals = np.asarray(js_mesh["Normals"], dtype=np.float32)
            np_normals.shape = (int(len(np_normals) / 3), 3)

        # Get UVs
        uvs_dict = {}

        if "UVs" in js_mesh.keys():
            for i, (js_uv_key, js_uv) in enumerate(js_mesh["UVs"].items()):
                # new_uv = np.asarray(js_uv, dtype=np.float32)
                # new_uv.shape = (int(len(new_uv) / 2), 2)
                new_uv = js_uv

                if i > 0:
                    uv_name = "UVMap" + js_uv_key.replace('UV', '')
                else:
                    uv_name = "UVMap"

                uvs_dict[uv_name] = new_uv

        # Get Vertex Colors
        np_colors = None

        if "VertexColors" in js_mesh.keys():
            # np_colors = np.asarray(js_mesh["VertexColors"], dtype=np.float32)
            np_colors = js_mesh["VertexColors"]
            # np_colors.shape = len(np_colors) * 4

        # Create Mesh
        new_mesh = CreateMesh(polys_len, np_verts, np_poly_indices, np_normals)

        # Setup Additional Mesh data

        # Setup UVs
        if len(uvs_dict.items()) > 0:
            for uv_name, uv in uvs_dict.items():
                uv_layer = new_mesh.uv_layers.new(name=uv_name)
                uv_layer.data.foreach_set('uv', uv)

        # Setup Vertex Colors
        if np_colors is not None:
            new_mesh.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
            new_mesh.attributes["Color"].data.foreach_set('color', np_colors)

    else:
        new_mesh = CreateEmptyMesh()

    return new_mesh


def CurvesFromJSON(js_obj, engine_type: EngineType, import_as_curve: bool):

    js_curv = js_obj["Curves"]
    js_curve_elems = js_curv["CurveElements"]

    if import_as_curve:
        be_curv_data = bpy.data.curves.new(js_obj["Name"], type='CURVE')
        be_curv_data.dimensions = '3D'
        # be_sub_curv.resolution_u = 2

        for js_curve_elem in js_curve_elems:

            # Create Spline
            verts_len = int(len(js_curve_elem["Verts"]) / 3)

            np_verts = np.asarray(js_curve_elem["Verts"], dtype=np.float32)
            np_verts.shape = (verts_len, 3)

            np_verts_2 = np.empty((len(np_verts), 1), dtype=np.float32)
            np_verts = np.append(np_verts, np_verts_2, axis=1)

            np_verts.shape = len(np_verts) * 4

            polyline = be_curv_data.splines.new('POLY')  # New Spline has 1 Point
            polyline.points.add(verts_len - len(polyline.points))  # Here we Substract 1 Point
            polyline.points.foreach_set('co', np_verts)

            # Set Open/Closed
            polyline.use_cyclic_u = js_curve_elem["IsClosed"]

    else:
        be_curv_data = bpy.data.meshes.new(js_obj["Name"])
        verts = []
        edges = []

        vert_counter = 0
        for js_curve_elem in js_curve_elems:

            curv_verts_len = int(len(js_curve_elem["Verts"]) / 3)

            np_verts = np.asarray(js_curve_elem["Verts"], dtype=np.float32)
            np_verts.shape = (curv_verts_len, 3)

            for i, vert in enumerate(np_verts):
                # Add Verts
                verts.append(vert)

                # Add Edges
                if curv_verts_len > 1:
                    if i != (curv_verts_len - 1):
                        edges.append((vert_counter, vert_counter + 1))
                    else:
                        if js_curve_elem["IsClosed"]:
                            edges.append((vert_counter, vert_counter - (curv_verts_len - 1)))

                vert_counter += 1

        be_curv_data.from_pydata(verts, edges, [])

    return be_curv_data


def TerrainMeshFromJSON(js_obj, engine_type: EngineType):
    js_terr = js_obj["Terrain"]

    if "Verts" in js_terr and js_terr["Verts"]:
        # verts_len = len(js_terr["Verts"])

        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=js_terr["NumberSegmentsX"], y_segments=js_terr["NumberSegmentsY"], calc_uvs=False)

        # verts_len = len(js_terr["Verts"])

        # np_verts = np.asarray(js_terr["Verts"], dtype=np.float32)
        np_verts = js_terr["Verts"]

        # bm.verts.foreach_set('co', np_verts)

        new_mesh = bpy.data.meshes.new("BESubMesh")
        bm.to_mesh(new_mesh)
        bm.free()

        new_mesh.vertices.foreach_set('co', np_verts)

        new_mesh.update()

        return new_mesh


def MeshToJSONData(mesh, engine_type: EngineType):
    mesh_dict = {}  # Instances Dictionary

    # Get Points
    np_verts = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', np_verts)

    mesh_dict["Verts"] = np_verts.tolist()

    # GET MESHES
    # MAIN Attributes

    # Get Polygons
    # poly_indices = [tuple(poly.vertices) for poly in mesh.polygons]
    poly_indices = [vert for poly in mesh.polygons for vert in poly.vertices]

    mesh_dict["PolyIndices"] = poly_indices

    # # Get Polygons Loops
    # poly_loops = [tuple(poly.loop_indices) for poly in mesh.polygons]
    # mesh_dict["Loops"] = poly_loops

    # Get Polygons Loop Start
    np_loop_start = np.empty(len(mesh.polygons), dtype=np.int32)
    mesh.polygons.foreach_get("loop_start", np_loop_start)
    mesh_dict["LoopStart"] = np_loop_start.tolist()

    # # Get Triangles Only
    # mesh.calc_loop_triangles()
    # np_tris = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
    # mesh.loop_triangles.foreach_get('vertices', np_tris)
    # np_tris.shape = (len(mesh.loop_triangles), 3)
    # mesh_dict["PolyIndices"] = np_tris.tolist()

    # # Get Loops of Triangles
    # np_tris_loops = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
    # mesh.loop_triangles.foreach_get('loops', np_tris_loops)
    # np_tris_loops.shape = (len(mesh.loop_triangles), 3)
    # mesh_dict["Loops"] = np_tris_loops.tolist()

    # Get Normals
    if BESettings.BENGINE_NORMAL in mesh.attributes.keys():
        normal_attr = mesh.attributes[BESettings.BENGINE_NORMAL]

        if normal_attr.domain == 'CORNER':
            if data_type == 'VECTOR':
                np_normals = np.empty(len(normal_attr.data) * 3, dtype=np.float32)
                normal_attr.data.foreach_get('vector', np_normals)
                # np_normals.shape = (len(normal_attr.data), 3)
            else:
                print("Attribute" + attrib_name + " has "
                      + data_type + " Type. It's not supported and passed. Standard Normals are used instead!!!")
                np_normals = GetMeshNormalsNumpy(mesh)
        else:
            print("Attribute " + BESettings.BENGINE_NORMAL + " must have FACECORNER domain. Taken Default Normals Instead!!!")
            np_normals = GetMeshNormalsNumpy(mesh)
    else:
        np_normals = GetMeshNormalsNumpy(mesh)

    mesh_dict["Normals"] = np_normals.tolist()

    # GET UVS, Colors, Materials
    uvs_dict = {}
    np_col_attrib = None

    # Get Attributes
    for attrib_name in mesh.attributes.keys():

        parsed_attr = mesh.attributes[attrib_name]
        data_type = parsed_attr.data_type

        # UVs
        if attrib_name in BESettings.UV_NAMES:

            if parsed_attr.domain == 'CORNER':
                
                if (len(parsed_attr.data) > 0):
                    if data_type == 'FLOAT_VECTOR':
                        uv_vec_len = 3
                    elif data_type == 'FLOAT2':
                        uv_vec_len = 2
                    else:
                        print("Attribute" + parsed_attr.name + " has "
                              + data_type + " Type. It's not supported and passed!!!")
                        continue

                    np_uv_attrib = np.empty(len(parsed_attr.data) * uv_vec_len, dtype=np.float32)
                    parsed_attr.data.foreach_get('vector', np_uv_attrib)

                    # Remove Third Coordinate
                    if uv_vec_len == 3 and len(np_uv_attrib) > 2:
                        # print(np_uv_attrib)
                        np_uv_attrib = np.delete(np_uv_attrib, np.arange(2, len(np_uv_attrib), 3))
                        # print(np_uv_attrib)

                    uvs_dict[attrib_name] = np_uv_attrib.tolist()

            else:
                print("Attribute " + attrib_name + " must be FACECORNER domain!!!")

        # Color
        elif attrib_name == BESettings.BENGINE_COLOR:

            if parsed_attr.domain == 'CORNER':

                if data_type != 'FLOAT_COLOR':
                    print("Attribute" + attrib_name + " has "
                            + data_type + " Type. It's not supported and passed!!!")
                    continue

                np_col_attrib = np.empty(len(parsed_attr.data) * 4, dtype=np.float32)
                parsed_attr.data.foreach_get('color', np_col_attrib)
                mesh_dict["VertexColors"] = np_col_attrib.tolist()
            else:
                print("Attribute " + attrib_name + " must be FACECORNER domain!!!")

        # Setup bengine_material Value
        elif attrib_name == BESettings.BENGINE_MATERIAL:
            if parsed_attr.domain == 'FACE':
                np_mat_attrib = np.empty(len(parsed_attr.data), dtype=np.uint8)
                parsed_attr.data.foreach_get('value', np_mat_attrib)
                mesh_dict["Materials"] = np_mat_attrib.tolist()
            else:
                print("Attribute " + attrib_name + " must be FACE domain!!!")

    if uvs_dict:
        mesh_dict["UVs"] = uvs_dict
    
    return mesh_dict


def GetMeshNormalsNumpy(mesh):

    # GET NORMALS
    if bpy.app.version[0] < 4 or (bpy.app.version[0] == 4 and bpy.app.version[1] == 0):
        # Calc Split Nomrals
        mesh.calc_normals_split()

        np_normals = np.empty(len(mesh.loops) * 3, dtype=np.float32)
        mesh.loops.foreach_get("normal", np_normals)
    
    # Blender 4.1+
    else:
        np_normals = np.empty(len(mesh.loops) * 3, dtype=np.float32)
        mesh.corner_normals.foreach_get("vector", np_normals)

    return np_normals


