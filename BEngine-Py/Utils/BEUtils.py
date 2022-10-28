import bpy

import sys
import os

import json
# from json.decoder import JSONDecodeError

import numpy as np

from math import degrees
from mathutils import Color, Vector, Euler

UV_NAMES = {"uv_map", "uv_map2", "uv_map3", "uv_map4", "uv_map5",
            "uv_map6", "uv_map7", "uv_map8", "uv_map9", "uv_map10"}

BENGINE_INSTANCE = "be_instance"
BENGINE_MATERIAL = "be_material"
BENGINE_COLOR = "be_color"

OUTPUT_JSON_NAME = "BlenderOutputs.json"

class BEPaths:

    def __init__(self):
        self.blendfile = ""
        self.blendfolder = ""
        self.section = "/NodeTree/"
        self.node_sys_name = ""
        self.be_tmp_folder = ""
        self.project_path = ""
        self.project_path_2 = ""

        args = sys.argv

        for arg in args:
            if arg.startswith('BLENDFILE='):
                self.blendfile = arg.replace('BLENDFILE=', '')

            elif arg.startswith('BLENDFOLDER='):
                self.blendfolder = arg.replace('BLENDFOLDER=', '')
                
                if not self.blendfolder.endswith('/'):
                    self.blendfolder = self.blendfolder + "/"

            elif arg.startswith('NODESYSNAME='):
                self.node_sys_name = arg.replace('NODESYSNAME=', '')

            elif arg.startswith('BE_TMP_FOLDER='):
                self.be_tmp_folder = arg.replace('BE_TMP_FOLDER=', '')
 
            elif arg.startswith('PROJECT_PATH='):
                self.project_path = arg.replace('PROJECT_PATH=', '')
 
            elif arg.startswith('PROJECT_PATH_2='):
                self.project_path_2 = arg.replace('PROJECT_PATH_2=', '')

        # blend file name
        self.blendfile_basename = os.path.basename(self.blendfile)
        self.blendfile_name = os.path.splitext(self.blendfile_basename)[0]

        # Load GN
        self.filepath = self.blendfile + self.section + self.node_sys_name
        self.directory = self.blendfile + self.section
        self.filename = self.node_sys_name


def SaveJSON(gn_js_path, js_data):
    with open(gn_js_path, 'w') as json_file:

        json.dump(js_data, json_file)


def ClearScene():
    # Clear Scene
    objs = bpy.data.objects
    for obj in objs:
        objs.remove(obj, do_unlink=True)

    meshes = bpy.data.meshes
    for mesh in meshes:
        meshes.remove(mesh, do_unlink=True)

    nodes = bpy.data.node_groups
    for node in nodes:
        nodes.remove(node, do_unlink=True)

    colls = bpy.data.collections
    for coll in colls:
        colls.remove(coll, do_unlink=True)

    mats = bpy.data.materials
    for mat in mats:
        mats.remove(mat, do_unlink=True)


def GetGNInputsData(node_group):
    gn_inputs_data = []

    for i, input in enumerate(node_group.inputs.items()):
        input_data = {}
        input_data['Type'] = input[1].type
        input_data['Name'] = input[1].name
        input_data['Identifier'] = input[1].identifier

        match input_data['Type']:
            case 'VALUE':
                input_data['DefaultValue'] = input[1].default_value
                # input_data['DefaultValue'] = numpy.float32(input[1].default_value)

                input_data['MinValue'] = input[1].min_value
                input_data['MaxValue'] = input[1].max_value

                # input_data['Value'] = geom_mod[input[1].identifier]

            case 'INT':
                input_data['DefaultValue'] = input[1].default_value

                input_data['MinValue'] = input[1].min_value
                input_data['MaxValue'] = input[1].max_value

            case _:
                if input_data['Type'] in {'STRING', 'BOOLEAN'}:
                    input_data['DefaultValue'] = input[1].default_value
                    # input_data['Value'] = geom_mod[input[1].identifier]

                elif input_data['Type'] in ('RGBA', 'VECTOR'):
                    input_data['DefaultValue'] = list(input[1].default_value)

        gn_inputs_data.append(input_data)

    return gn_inputs_data


def LoadGN(context, be_paths: BEPaths):

    bpy.ops.wm.link(filepath=be_paths.filepath, filename=be_paths.filename, directory=be_paths.directory)

    if (bpy.data.node_groups):
        bengine_GN = bpy.data.node_groups[be_paths.node_sys_name]

        # Create New Object
        process_mesh = bpy.data.meshes.new('emptyMesh')
        process_obj = bpy.data.objects.new("BEngineProcess", process_mesh)

        context.collection.objects.link(process_obj)

        process_obj.select_set(True)
        context.view_layer.objects.active = process_obj

        # Add GN Modifier
        geom_mod = process_obj.modifiers.new("BEngine", type='NODES')
        # geom_mod.show_viewport = False  # Modifier is switched off during loading
        geom_mod.node_group = bengine_GN

        return process_obj, geom_mod, bengine_GN
    
    return None, None, None


def SetupInputsFromJSON(context, bengine_GN, geom_mod, js_input_data,
                        be_paths: BEPaths, engine_type: str):

    coll_idx = 0

    for input in bengine_GN.inputs.items():
        input_data = {}
        input_data['Type'] = input[1].type
        input_data['Name'] = input[1].name
        input_data['Identifier'] = input[1].identifier

        if input[1].identifier in js_input_data.keys() and input[1].type == js_input_data[input[1].identifier]["Type"]:
            
            prop = js_input_data[input[1].identifier]

            if "Value" in prop.keys() and prop["Value"] is not None:

                match prop["Type"]:
                    case "RGBA":
                        prop_value = prop["Value"]

                    case "VECTOR":
                        prop_value = prop["Value"]

                    case "IMAGE":
                        new_img = bpy.data.images.load(be_paths.project_path_2 + prop["Value"])
                        prop_value = new_img

                    # case "TEXTURE":
                    #     pass

                    case "MATERIAL":
                        mat = bpy.data.materials.new(name="BEMaterial")
                        prop_value = mat

                    case "OBJECT":
                        js_obj_val = prop["Value"]

                        be_objs, has_mesh = ParseObjectFromJSON(context, js_obj_val, engine_type, False, True)

                        # Join Meshes
                        bpy.ops.object.select_all(action='DESELECT')

                        be_obj = None

                        if len(be_objs) > 1:
                            be_obj = be_objs[0]

                            for obj in be_objs:
                                context.collection.objects.link(obj)
                                obj.select_set(True)

                            context.view_layer.objects.active = be_obj
                            bpy.ops.object.join()

                        else:
                            if len(be_objs) == 1:
                                be_obj = be_objs[0]
                                context.collection.objects.link(be_objs[0])

                        prop_value = be_obj

                    case "COLLECTION":
                        js_coll_val = prop["Value"]

                        be_coll = bpy.data.collections.new('BEngine_' + str(coll_idx))
                        context.scene.collection.children.link(be_coll)

                        be_coll_objs, has_mesh = ParseObjectFromJSON(context, js_coll_val, engine_type, True, False)

                        for obj in be_coll_objs:
                            be_coll.objects.link(obj)

                        prop_value = be_coll

                        coll_idx += 1

                    case "VALUE":
                        prop_value = float(prop["Value"])

                    case default:
                        prop_value = prop["Value"]

                #  Set Property Value
                if prop["Type"] == "VECTOR":
                    geom_mod[input[1].identifier][0] = prop_value[0]
                    geom_mod[input[1].identifier][1] = prop_value[1]
                    geom_mod[input[1].identifier][2] = prop_value[2]

                elif prop["Type"] == "RGBA":
                    geom_mod[input[1].identifier][0] = prop_value[0]
                    geom_mod[input[1].identifier][1] = prop_value[1]
                    geom_mod[input[1].identifier][2] = prop_value[2]
                    geom_mod[input[1].identifier][3] = prop_value[3]

                else:
                    geom_mod[input[1].identifier] = prop_value


def ParseObjectFromJSON(context, js_obj_val, engine_type: str, isCollection: bool, convert_to_meshes=False):
    has_mesh = False

    be_objs = []

    # Check If it has Mesh
    for js_obj in js_obj_val:
        if "Mesh" in js_obj and "Verts" in js_obj["Mesh"] and js_obj["Mesh"]["Verts"]:
            has_mesh = True
            break

    # if hasMesh:
    for i, js_obj in enumerate(js_obj_val):
        be_mesh_obj = None
        be_curves_obj = None

        # # pass 0 index if it's Collection
        # if isCollection and i == 0:
        #     continue

        # Import Mesh
        if "Mesh" in js_obj:
            be_mesh_obj = ImportMeshFromJSON(context, js_obj, engine_type)
            be_objs.append(be_mesh_obj)

        # Import Curves
        if "Curves" in js_obj:
            if (convert_to_meshes):
                be_curves_obj = ImportCurvesFromJSON(context, js_obj, engine_type, bool(1 - has_mesh))
            else:
                be_curves_obj = ImportCurvesFromJSON(context, js_obj, engine_type, True)

            be_objs.append(be_curves_obj)

        if be_mesh_obj is None and be_curves_obj is None:
            if isCollection:
                # Add Empty
                empty_obj = bpy.data.objects.new(js_obj["Name"], None )
                SetTransformFromJSON(js_obj, empty_obj, engine_type)
                be_objs.append(empty_obj)

            else:
                # Add an Empty Object which will be as a Master Object to Joint all Objects
                if i == 0:
                    be_empty_main_obj = None

                    if has_mesh:
                        empty_mesh_data = bpy.data.meshes.new('BESubMesh')
                        be_empty_main_obj = bpy.data.objects.new(js_obj["Name"], empty_mesh_data)
                    else:
                        empty_curv_data = bpy.data.curves.new(js_obj["Name"], type='CURVE')
                        empty_curv_data.dimensions = '3D'

                        be_empty_main_obj = bpy.data.objects.new(js_obj["Name"], empty_curv_data)

                    SetTransformFromJSON(js_obj, be_empty_main_obj, engine_type)

                    be_objs.append(be_empty_main_obj)

    return be_objs, has_mesh


def ImportMeshFromJSON(context, js_obj, engine_type: str):
    js_mesh = js_obj["Mesh"]

    if "Verts" in js_mesh and js_mesh["Verts"]:
        verts_len = len(js_mesh["Verts"])
        polys_len = len(js_mesh["PolyIndices"])

        np_verts = np.asarray(js_mesh["Verts"], dtype=np.float32)
        np_verts.shape = len(np_verts) * 3

        np_poly_indices = np.asarray(js_mesh["PolyIndices"], dtype=np.int32)
        np_poly_indices.shape = polys_len * 3

        np_normals = np.asarray(js_mesh["Normals"], dtype=np.float32)
        # np_normals.shape = len(js_mesh["Normals"]) * 3

        # Get UVs
        uvs_dict = {}

        if "UVs" in js_mesh.keys():
            for i, (js_uv_key, js_uv) in enumerate(js_mesh["UVs"].items()):
                # new_uv = np.asarray(js_uv, dtype=np.float32)

                # new_uv = [js_uv[loop.vertex_index] for loop in be_sub_mesh.loops]
                new_uv = [js_uv[idx] for idx in np_poly_indices]
                new_uv = np.asarray(new_uv, dtype=np.float32)
                new_uv.shape = len(new_uv) * 2

                if i > 0:
                    uv_name = "UVMap" + js_uv_key.replace('UV', '')
                else:
                    uv_name = ""

                uvs_dict[uv_name] = new_uv

        # Get Vertex Colors
        np_colors = None

        if "VertexColors" in js_mesh.keys():
            np_colors = np.asarray(js_mesh["VertexColors"], dtype=np.float32)
            np_colors.shape = len(np_colors) * 4

        # Create Mesh
        new_mesh = CreateMesh(verts_len, polys_len, 
                                np_verts, np_poly_indices, np_normals)

        # Setup Additiona Mesh data

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
        new_mesh = bpy.data.meshes.new('BESubMesh')

    be_mesh_obj = bpy.data.objects.new(js_obj["Name"], new_mesh)

    SetTransformFromJSON(js_obj, be_mesh_obj, engine_type)

    # context.collection.objects.link(be_mesh_obj)

    return be_mesh_obj


def ImportCurvesFromJSON(context, js_obj, engine_type: str, import_as_curve: bool):

    js_curv = js_obj["Curves"]
    js_curve_elems = js_curv["CurveElements"]

    if import_as_curve:
        be_curv_data = bpy.data.curves.new(js_obj["Name"], type='CURVE')
        be_curv_data.dimensions = '3D'
        # be_sub_curv.resolution_u = 2

        for js_curve_elem in js_curve_elems:

            # Create Spline
            verts_len = len(js_curve_elem["Verts"])

            np_verts = np.asarray(js_curve_elem["Verts"], dtype=np.float32)
            np_verts_2 = np.zeros((len(np_verts), 1), dtype=np.float32)
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

            curv_verts_len = len(js_curve_elem["Verts"])

            for i, vert in enumerate(js_curve_elem["Verts"]):
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

    # Add Curve Object
    be_curve_obj = bpy.data.objects.new(js_obj["Name"], be_curv_data)

    SetTransformFromJSON(js_obj, be_curve_obj, engine_type)

    return be_curve_obj


# Create Mesh
def CreateMesh(verts_len, polys_len, np_verts, np_poly_indices, np_normals):
    mesh = bpy.data.meshes.new('BESubMesh')

    mesh.vertices.add(verts_len)
    mesh.vertices.foreach_set('co', np_verts)

    mesh.polygons.add(polys_len)

    mesh.loops.add(polys_len * 3)
    mesh.loops.foreach_set("vertex_index", np_poly_indices)

    np_loop_start = np.arange(0, (polys_len * 3) - 1, 3, dtype=np.int32)
    mesh.polygons.foreach_set('loop_start', np_loop_start)

    np_loops_total = np.full(polys_len, 3, dtype=np.int32)
    mesh.polygons.foreach_set('loop_total', np_loops_total)

    # Smooth
    np_smooth = np.full(polys_len, 1, dtype=np.int8)
    mesh.polygons.foreach_set("use_smooth", np_smooth)

    mesh.use_auto_smooth = True

    # be_sub_mesh.validate()
    mesh.update()

    # Normals
    mesh.normals_split_custom_set_from_vertices(np_normals)
    # normals2 = [js_mesh["Normals"][loop.vertex_index] for loop in be_sub_mesh.loops]
    # be_sub_mesh.normals_split_custom_set(normals2)

    return mesh


def SetTransformFromJSON(js_obj, be_obj, engine_type: str):
    be_obj.location = js_obj["Pos"]
    SetRotationFromJSON(be_obj, js_obj["Rot"], engine_type)
    be_obj.scale = js_obj["Scale"]


def SaveBlenderOutputs(context, process_obj, be_paths: BEPaths, engine_type: str):

    depsgraph = context.evaluated_depsgraph_get()
    process_obj_ev = depsgraph.objects[process_obj.name]

    # MAIN Data
    js_output_data = {}  # Output JSON Data
    inst_dict = {}  # Instances Dictionary
    meshes = []  # All Meshes
    
    # GET INSTANCES
    for object_instance in depsgraph.object_instances:
        if object_instance.parent is process_obj_ev and object_instance.is_instance:
            inst_data = object_instance.object.data

            if inst_data not in inst_dict.keys():
                inst_dict[inst_data] = {}
                inst_dict[inst_data]["Transforms"] = []

            cur_inst_data = inst_dict[inst_data]

            # Setup Transforms
            inst_pos, inst_rot, inst_scale = object_instance.matrix_world.decompose()
            # inst_pos_loc, inst_rot_loc, inst_scale_loc = object_instance.object.matrix_local.decompose()

            cur_inst_data["Transforms"].append((tuple(inst_pos), tuple(inst_rot.to_euler('XYZ')), tuple(inst_scale)))

            # Setup bengine_instance Value and Mesh
            if object_instance.object.type == "MESH":
                if BENGINE_INSTANCE in inst_data.attributes.keys():
                    if BENGINE_INSTANCE not in cur_inst_data.keys():
                        if len(inst_data.attributes[BENGINE_INSTANCE].data) > 0:
                            cur_inst_data["Bengine_Instance"] = inst_data.attributes[BENGINE_INSTANCE].data[0].value
                else:
                    if "Mesh" not in cur_inst_data.keys():
                        # GET INSTANCE MESH
                        cur_inst_data["Mesh"] = MeshToJSONData(object_instance.object)

    js_output_data["Instances"] = list(inst_dict.values())

    # GET MAIN MESH
    mesh_dict = MeshToJSONData(process_obj_ev)

    # Only one mesh at the moment
    if len(mesh_dict["Verts"]) > 0:
        meshes.append(mesh_dict)

    if meshes:
        js_output_data["Meshes"] = meshes

    gn_js_path = be_paths.be_tmp_folder + OUTPUT_JSON_NAME

    SaveJSON(gn_js_path, js_output_data)


def MeshToJSONData(process_obj):
    mesh_dict = {}  # Instances Dictionary

    # Get Points
    np_verts = np.zeros(len(process_obj.data.vertices) * 3, dtype=np.float32)
    process_obj.data.vertices.foreach_get('co', np_verts)
    np_verts.shape = (len(process_obj.data.vertices), 3)
    mesh_dict["Verts"] = np_verts.tolist()

    # GET MESHES
    # MAIN Attributes

    # Get Polygons
    poly_indices = [tuple(poly.vertices) for poly in process_obj.data.polygons]
    mesh_dict["PolyIndices"] = poly_indices

    # # Get Polygons Loops
    # poly_loops = [tuple(poly.loop_indices) for poly in process_obj.data.polygons]
    # mesh_dict["Loops"] = poly_loops

    # Get Polygons Loop Start
    np_loop_start = np.empty(len(process_obj.data.polygons), dtype=np.int32)
    process_obj.data.polygons.foreach_get("loop_start", np_loop_start)
    mesh_dict["LoopStart"] = np_loop_start.tolist()

    # # Get Triangles Only
    # process_obj.data.calc_loop_triangles()
    # np_tris = np.zeros(len(process_obj.data.loop_triangles) * 3, dtype=np.int32)
    # process_obj.data.loop_triangles.foreach_get('vertices', np_tris)
    # np_tris.shape = (len(process_obj.data.loop_triangles), 3)
    # mesh_dict["PolyIndices"] = np_tris.tolist()

    # # Get Loops of Triangles
    # np_tris_loops = np.zeros(len(process_obj.data.loop_triangles) * 3, dtype=np.int32)
    # process_obj.data.loop_triangles.foreach_get('loops', np_tris_loops)
    # np_tris_loops.shape = (len(process_obj.data.loop_triangles), 3)
    # mesh_dict["Loops"] = np_tris_loops.tolist()

    # calc split nomrals
    process_obj.data.calc_normals_split()

    # GET NORMALS
    np_normals = np.zeros(len(process_obj.data.loops) * 3, dtype=np.float32)
    process_obj.data.loops.foreach_get("normal", np_normals)
    np_normals.shape = (len(process_obj.data.loops), 3)
    mesh_dict["Normals"] = np_normals.tolist()

    # GET UVS, Colors, Materials
    uvs_dict = {}
    np_col_attrib = None

    for attrib_name in process_obj.data.attributes.keys():
        if attrib_name in UV_NAMES:

            if process_obj.data.attributes[attrib_name].domain == 'CORNER':
                if (len(process_obj.data.attributes[attrib_name].data) > 0):

                    # if process_obj.data.attributes[attrib_name].data_type == 'FLOAT':
                    #     uv_vec_len = 2
                    # else:
                    uv_vec_len = len(process_obj.data.attributes[attrib_name].data[0].vector)

                    np_uv_attrib = np.zeros(len(process_obj.data.attributes[attrib_name].data) * uv_vec_len, dtype=np.float32)

                    # if process_obj.data.attributes[attrib_name].data_type == 'FLOAT':
                    #     process_obj.data.attributes[attrib_name].data.foreach_get('value', np_uv_attrib)
                    # else:
                    process_obj.data.attributes[attrib_name].data.foreach_get('vector', np_uv_attrib)
                    
                    np_uv_attrib.shape = (len(process_obj.data.attributes[attrib_name].data), uv_vec_len)

                    uvs_dict[attrib_name] = np_uv_attrib.tolist()

            else:
                print("Attribute " + attrib_name + "must have FACECORNER domain!!!")

        elif attrib_name == BENGINE_COLOR:

            if process_obj.data.attributes[attrib_name].domain == 'CORNER':
                # col_attrib = [tuple(uv_attr.color) for uv_attr in process_obj_ev.data.attributes[attrib_name].data]
                # mesh_dict["VertexColor"] = col_attrib

                np_col_attrib = np.zeros(len(process_obj.data.attributes[attrib_name].data) * 4, dtype=np.float32)
                process_obj.data.attributes[attrib_name].data.foreach_get('color', np_col_attrib)
                np_col_attrib.shape = (len(process_obj.data.attributes[attrib_name].data), 4)
                mesh_dict["VertexColors"] = np_col_attrib.tolist()
            else:
                print("Attribute " + attrib_name + "must have FACECORNER domain!!!")

        # Setup bengine_material Value
        elif attrib_name == BENGINE_MATERIAL:
            if process_obj.data.attributes[attrib_name].domain == 'FACE':
                np_mat_attrib = np.zeros(len(process_obj.data.attributes[attrib_name].data), dtype=np.uint8)
                process_obj.data.attributes[attrib_name].data.foreach_get('value', np_mat_attrib)
                mesh_dict["Materials"] = np_mat_attrib.tolist()
            else:
                print("Attribute " + attrib_name + "must have FACE domain!!!")

    if uvs_dict:
        mesh_dict["UVs"] = uvs_dict
    
    return mesh_dict


def SetRotationFromJSON(obj, js_euler, engine_type: str):
    if engine_type == "Unity":
        # Set Rotation
        rot_YXZ = Euler(js_euler, 'YXZ')
        rot_mat = rot_YXZ.to_matrix()
        rot_XYZ = rot_mat.to_euler('XYZ')

        obj.rotation_euler = rot_XYZ

    else:
        obj.rotation_euler = js_euler