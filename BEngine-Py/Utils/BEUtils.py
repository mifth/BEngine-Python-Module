import bpy

import sys
import os

import json
from json.decoder import JSONDecodeError

import numpy as np

from math import degrees
from mathutils import Color, Vector, Euler

import bmesh
import mathutils


UV_NAMES = {"uv_map", "uv_map2", "uv_map3", "uv_map4", "uv_map5",
            "uv_map6", "uv_map7", "uv_map8", "uv_map9", "uv_map10"}

BENGINE_INSTANCE = "be_instance"
BENGINE_MATERIAL = "be_material"
BENGINE_COLOR = "be_color"
BENGINE_NORMAL = "be_normal"

TYPE_GN = "GeometryNodeTree"
TYPE_SV = "SverchCustomTreeType"
TYPE_SV_SCRIPT = "SvScriptNodeLite"

OUTPUT_JSON_NAME = "BlenderOutputs.json"


class SVConstants:
    SV_INPUT_BOOL = "BEBoolean.py"
    SV_INPUT_COLL = "BECollection.py"
    SV_INPUT_COLOR = "BEColor.py"
    SV_INPUT_FLOAT = "BEFloat.py"
    SV_INPUT_INT = "BEInteger.py"
    SV_INPUT_OBJ = "BEObject.py"
    SV_INPUT_STR = "BEString.py"
    SV_INPUT_VEC = "BEVector.py"

    SV_Inputs = (SV_INPUT_BOOL, SV_INPUT_COLL, SV_INPUT_COLOR, 
                    SV_INPUT_FLOAT, SV_INPUT_INT, SV_INPUT_OBJ,
                    SV_INPUT_STR, SV_INPUT_VEC)

    SV_OUTPUT_OBJ = "BEObjectsOutput.py"


class BEProjectPaths:

    def __init__(self):
        self.be_tmp_folder = None
        self.project_path = None
        self.project_path_2 = None

        self.run_blender_Type = None
        self.host = None
        self.port = None
        self.max_package_bytes = None

        args = sys.argv

        for arg in args:
            if arg.startswith('BE_TMP_FOLDER='):
                self.be_tmp_folder = arg.replace('BE_TMP_FOLDER=', '')
            elif arg.startswith('PROJECT_PATH='):
                self.project_path = arg.replace('PROJECT_PATH=', '')
            elif arg.startswith('PROJECT_PATH_2='):
                self.project_path_2 = arg.replace('PROJECT_PATH_2=', '')

        # # Networking
            elif arg.startswith('RunBlenderType='):
                self.run_blender_Type = arg.replace('RunBlenderType=', '')
            elif arg.startswith('Host='):
                self.host = arg.replace('Host=', '')
            elif arg.startswith('Port='):
                self.port = int(arg.replace('Port=', ''))
            elif arg.startswith('MaxPackageBytes='):
                self.max_package_bytes = int(arg.replace('MaxPackageBytes=', ''))


class BEBaseStuff:

    def __init__(self, be_paths: dict):
        self.section = "/NodeTree/"
        self.blendfile = ""
        self.blendfolder = ""
        self.node_sys_name = ""

        # if arg.startswith('BLENDFILE='):
        self.blendfile = be_paths["BLENDFILE"]

        # elif arg.startswith('BLENDFOLDER='):
        self.blendfolder = be_paths["BLENDFOLDER"]
        if not self.blendfolder.endswith('/'):
            self.blendfolder = self.blendfolder + "/"

        # elif arg.startswith('NODESYSNAME='):
        self.node_sys_name = be_paths["NODESYSNAME"]

        # blend file name
        self.blendfile_basename = os.path.basename(self.blendfile)
        self.blendfile_name = os.path.splitext(self.blendfile_basename)[0]

        # Load GN Paths
        self.filepath = self.blendfile + self.section + self.node_sys_name
        self.directory = self.blendfile + self.section
        self.filename = self.node_sys_name

        self.be_type = be_paths["BEngineType"]

        # # Networking
        # self.RunBlenderType = be_paths["RunBlenderType"]
        # self.Host = be_paths["Host"]
        # self.Port = be_paths["Port"]
        # self.MaxPackageBytes = be_paths["MaxPackageBytes"]


def LoadJSON(bengineInputs_path: str):
    with open(bengineInputs_path) as js_file:
        try:
            js_input_data = json.load(js_file)
        except JSONDecodeError:
            print("Problem to Open File: " + bengineInputs_path)
            js_input_data = None

    return js_input_data


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


# Set GN/SV Default/Min/Max Values
# input is either GNNodeInputs or SVNode
def SetBaseInputValues(input_data, input, is_GN: bool):
    match input_data['Type']:
        case 'VALUE':
            if is_GN:
                input_data['DefaultValue'] = input[1].default_value
                # input_data['DefaultValue'] = numpy.float32(input[1].default_value)

                input_data['MinValue'] = input[1].min_value
                input_data['MaxValue'] = input[1].max_value

                # input_data['Value'] = geom_mod[input[1].identifier]
            else:
                input_data['DefaultValue'] = input['BEFloatDefault']
                input_data['MinValue'] = input['BEFloatMin']
                input_data['MaxValue'] = input['BEFloatMax']

        case 'INT':
            if is_GN:
                input_data['DefaultValue'] = input[1].default_value
                input_data['MinValue'] = input[1].min_value
                input_data['MaxValue'] = input[1].max_value
            else:
                input_data['DefaultValue'] = input['BEIntegerDefault']
                input_data['MinValue'] = input['BEIntegerMin']
                input_data['MaxValue'] = input['BEIntegerMax']

        case 'BOOLEAN':
            if is_GN:
                input_data['DefaultValue'] = input[1].default_value
            else:
                input_data['DefaultValue'] = input['BEBooleanDefault']

        case 'STRING':
            if is_GN:
                input_data['DefaultValue'] = input[1].default_value
            else:
                input_data['DefaultValue'] = input['BEStringDefault']

        case 'RGBA':
            if is_GN:
                input_data['DefaultValue'] = list(input[1].default_value)
            else:
                input_data['DefaultValue'] = list(input['BEColorDefault'])

        case 'VECTOR':
            if is_GN:
                input_data['DefaultValue'] = list(input[1].default_value)
                input_data['MinValue'] = input[1].min_value
                input_data['MaxValue'] = input[1].max_value
            else:
                input_data['DefaultValue'] = list(input['BEVectorDefault'])
                input_data['DefaultValue'] = input['BEVectorMin']
                input_data['DefaultValue'] = input['BEVectorMax']


def GetSVOutputObjects(node_tree):
    sv_out_nodes = []
    sv_out_objs = []

    for node in node_tree.nodes:
        if node.bl_idname == TYPE_SV_SCRIPT:
            if SVConstants.SV_OUTPUT_OBJ in node.script_name:
                sv_out_nodes.append(node)

    sv_out_nodes.sort(key=lambda x: x.location.y)
    sv_out_nodes.reverse()

    for node in sv_out_nodes:
        try:
            socket_objs = node.inputs[0].sv_get(default=None)
            sv_out_objs += socket_objs
        except:
            print("No Objects/Meshes in BEObjectsOutput Node: " + node.name)

    return sv_out_objs


def GetSVInputNodes(node_tree):
    sv_input_nodes = []

    for node in node_tree.nodes:
        if node.bl_idname == TYPE_SV_SCRIPT:
            for in_out_name in SVConstants.SV_Inputs:
                if in_out_name in node.script_name:
                    the_name = ''

                    # Set Type
                    match in_out_name:
                        case SVConstants.SV_INPUT_BOOL:
                            the_name = 'BOOLEAN'
                        case SVConstants.SV_INPUT_COLL:
                            the_name = 'COLLECTION'
                        case SVConstants.SV_INPUT_COLOR:
                            the_name = 'RGBA'
                        case SVConstants.SV_INPUT_FLOAT:
                            the_name = 'VALUE'
                        case SVConstants.SV_INPUT_INT:
                            the_name = 'INT'
                        case SVConstants.SV_INPUT_OBJ:
                            the_name = 'OBJECT'
                        case SVConstants.SV_INPUT_STR:
                            the_name = 'STRING'
                        case SVConstants.SV_INPUT_VEC:
                            the_name = 'VECTOR'

                    sv_input_nodes.append((the_name, node))
                    break

    sv_input_nodes.sort(key=lambda x: x[1].location.y)
    sv_input_nodes.reverse()

    return sv_input_nodes


def GetSVInputsData(node_group):   # ADD IMAGE AND MATERIAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    sv_inputs_data = []

    sv_input_nodes = GetSVInputNodes(node_group)

    for sv_node_stuff in sv_input_nodes:
        sv_node = sv_node_stuff[1]
        input_data = {}

        input_data['Name'] = sv_node['BEInputName']
        input_data['Identifier'] = sv_node.node_id
        input_data['Type'] = sv_node_stuff[0]

        # Set Default/Min/Max Values
        SetBaseInputValues(input_data, sv_node, False)

        sv_inputs_data.append(input_data)

    return sv_inputs_data


def GetGNInputsData(node_group):
    gn_inputs_data = []

    for input in node_group.inputs.items():
        input_data = {}
        input_data['Type'] = input[1].type
        input_data['Name'] = input[1].name
        input_data['Identifier'] = input[1].identifier

        # Set Default/Min/Max Values
        SetBaseInputValues(input_data, input, True)

        gn_inputs_data.append(input_data)

    return gn_inputs_data


def LoadNodesTreeFromJSON(context, be_paths: BEProjectPaths, be_base_stuff: BEBaseStuff):

    bpy.ops.wm.link(filepath=be_base_stuff.filepath, filename=be_base_stuff.filename,
                    directory=be_base_stuff.directory, link=False)

    if (bpy.data.node_groups):
        node_tree = bpy.data.node_groups[be_base_stuff.node_sys_name]

        process_gn_obj = None
        geom_mod = None

        # If GN NodeTree
        if node_tree.bl_idname == TYPE_GN:
            # Create New Object
            process_mesh = bpy.data.meshes.new('emptyMesh')
            process_gn_obj = bpy.data.objects.new("BEngineProcess", process_mesh)

            context.collection.objects.link(process_gn_obj)

            process_gn_obj.select_set(True)
            context.view_layer.objects.active = process_gn_obj

            # Add GN Modifier
            geom_mod = process_gn_obj.modifiers.new("BEngine", type='NODES')
            # geom_mod.show_viewport = False  # Modifier is switched off during loading
            geom_mod.node_group = node_tree

        # else:
        #     # Switch Off Auto Update
        #     node_tree.sv_process = False

        return process_gn_obj, geom_mod, node_tree
    
    return None, None, None


def SetupInputsFromJSON(context, node_tree, GN_mod, js_input_data,
                        be_paths: BEProjectPaths, engine_type: str):

    js_inputs = js_input_data["BEngineInputs"]

    is_GN = node_tree.bl_idname == TYPE_GN

    coll_idx = 0

    # GN - Inputs
    # SV - SVInputNodes
    if is_GN:
        input_items = node_tree.inputs.items()
    else:
        input_items = GetSVInputNodes(node_tree)

    instanced_meshes = {}

    for input in input_items:

        if is_GN:
            node_id = input[1].identifier
        else:
            node_id = input[1].node_id

        if node_id in js_inputs.keys():

            # Check if the same type
            if is_GN:
                is_same_type = (input[1].type == js_inputs[node_id]["Type"])

                if not is_same_type:
                    print("!Input " + input[1].name + " is not the same type! " + input[1].type + " " + js_inputs[node_id]["Type"])
                    continue

            else:
                is_same_type = (input[0] == js_inputs[node_id]["Type"])

                if not is_same_type:
                    print("!Input " + input[1].name + " is not the same type! " + input[0] + " " + js_inputs[node_id]["Type"])
                    continue

            # Run Main Stuff
            js_prop = js_inputs[node_id]

            if "Value" in js_prop.keys() and js_prop["Value"] is not None:

                match js_prop["Type"]:
                    case "RGBA":
                        if is_GN:
                            GN_mod[input[1].identifier][0] = js_prop["Value"][0]
                            GN_mod[input[1].identifier][1] = js_prop["Value"][1]
                            GN_mod[input[1].identifier][2] = js_prop["Value"][2]
                            GN_mod[input[1].identifier][3] = js_prop["Value"][3]
                        else:
                            input[1]['BEColor'][0] = js_prop["Value"][0]
                            input[1]['BEColor'][1] = js_prop["Value"][1]
                            input[1]['BEColor'][2] = js_prop["Value"][2]
                            input[1]['BEColor'][3] = js_prop["Value"][3]

                    case "VECTOR":
                        if is_GN:
                            GN_mod[input[1].identifier][0] = js_prop["Value"][0]
                            GN_mod[input[1].identifier][1] = js_prop["Value"][1]
                            GN_mod[input[1].identifier][2] = js_prop["Value"][2]
                        else:
                            input[1]['BEVector'][0] = js_prop["Value"][0]
                            input[1]['BEVector'][1] = js_prop["Value"][1]
                            input[1]['BEVector'][2] = js_prop["Value"][2]

                    case "IMAGE":
                        new_img = bpy.data.images.load(be_paths.project_path_2 + js_prop["Value"])

                        if is_GN:
                            GN_mod[input[1].identifier] = new_img

                    # case "TEXTURE":
                    #     pass

                    case "MATERIAL":
                        mat = bpy.data.materials.new(name="BEMaterial")

                        if is_GN:
                            GN_mod[input[1].identifier] = mat

                    case "OBJECT":
                        js_obj_val = js_prop["Value"]

                        be_objs, has_mesh = ParseObjectFromJSON(context, js_obj_val,
                                                                js_input_data, instanced_meshes,
                                                                engine_type, False, True)

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

                        if is_GN:
                            GN_mod[input[1].identifier] = be_obj
                        else:
                            input[1]['BEObject'] = be_obj.name

                    case "COLLECTION":
                        js_coll_val = js_prop["Value"]

                        be_coll = bpy.data.collections.new('BEngine_' + str(coll_idx))
                        context.scene.collection.children.link(be_coll)

                        be_coll_objs, has_mesh = ParseObjectFromJSON(context, js_coll_val,
                                                                     js_input_data, instanced_meshes,
                                                                     engine_type, True, False)

                        for obj in be_coll_objs:
                            be_coll.objects.link(obj)

                        if is_GN:
                            GN_mod[input[1].identifier] = be_coll
                        else:
                            input[1]['BECollection'] = be_coll.name

                        coll_idx += 1

                    case "VALUE":
                        if is_GN:
                            GN_mod[input[1].identifier] = float(js_prop["Value"])
                        else:
                            input[1]['BEFloat'] = float(js_prop["Value"])

                    case "INT":
                        if is_GN:
                            GN_mod[input[1].identifier] = js_prop["Value"]
                        else:
                            input[1]['BEInteger'] = js_prop["Value"]

                    case "STRING":
                        if is_GN:
                            GN_mod[input[1].identifier] = js_prop["Value"]
                        else:
                            input[1]['BEString'] = js_prop["Value"]

                    case "BOOLEAN":
                        if is_GN:
                            GN_mod[input[1].identifier] = js_prop["Value"]
                        else:
                            input[1]['BEBoolean'] = js_prop["Value"]

                    case default:
                        if is_GN:
                            GN_mod[input[1].identifier] = js_prop["Value"]

                # else:
                #     GN_mod[input[1].identifier] = prop_value


def ParseObjectFromJSON(context, js_obj_val, js_input_data, instanced_meshes,
                        engine_type: str, isCollection: bool,
                        convert_to_meshes=False):
    has_mesh = False

    be_objs = []

    # Check If it has Mesh
    for js_obj in js_obj_val:
        if "Mesh" in js_obj or "Terrain" in js_obj:
            has_mesh = True
            break

    # if hasMesh:
    for i, js_obj in enumerate(js_obj_val):
        be_mesh_obj = None
        be_curves_obj = None
        be_terr_obj = None

        # Import Mesh
        if "Mesh" in js_obj:
            if js_obj["Mesh"] not in instanced_meshes.keys():
                js_mesh = js_input_data["Meshes"][js_obj["Mesh"]]
                be_mesh = MeshFromJSON(js_mesh, engine_type)

                instanced_meshes[js_obj["Mesh"]] = be_mesh
            else:
                be_mesh = instanced_meshes[js_obj["Mesh"]]

            be_mesh_obj = ObjectFromJSON(js_obj, be_mesh, engine_type, True)

            be_objs.append(be_mesh_obj)

        # Import Curves
        if "Curves" in js_obj:
            if (convert_to_meshes):
                be_curves_data = CurvesFromJSON(js_obj, engine_type, bool(1 - has_mesh))
            else:
                be_curves_data = CurvesFromJSON(js_obj, engine_type, True)

            be_curves_obj = ObjectFromJSON(js_obj, be_curves_data, engine_type, True)

            be_objs.append(be_curves_obj)

        # Import Terrain
        if "Terrain" in js_obj:
            be_terr_mesh = TerrainMeshFromJSON(js_obj, engine_type)
            be_terr_obj = ObjectFromJSON(js_obj, be_terr_mesh, engine_type, False)

            be_objs.append(be_terr_obj)

        if be_mesh_obj is None and be_curves_obj is None and be_terr_obj is None:
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

    instanced_meshes = None  # Clear Meshes

    return be_objs, has_mesh


def MeshFromJSON(js_mesh, engine_type: str):

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

    # context.collection.objects.link(be_mesh_obj)

    return new_mesh


def CurvesFromJSON(js_obj, engine_type: str, import_as_curve: bool):

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

    return be_curv_data


def TerrainMeshFromJSON(js_obj, engine_type: str):
    js_terr = js_obj["Terrain"]

    if "Verts" in js_terr and js_terr["Verts"]:
        verts_len = len(js_terr["Verts"])

        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=js_terr["NumberSegmentsX"], y_segments=js_terr["NumberSegmentsY"], calc_uvs=False)

        verts_len = len(js_terr["Verts"])

        np_verts = np.asarray(js_terr["Verts"], dtype=np.float32)
        np_verts.shape = len(np_verts) * 3

        # bm.verts.foreach_set('co', np_verts)

        new_mesh = bpy.data.meshes.new("BESubMesh")
        bm.to_mesh(new_mesh)
        bm.free()

        new_mesh.vertices.foreach_set('co', np_verts)

        new_mesh.update()

        return new_mesh


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


def ObjectFromJSON(js_obj, mesh, engine_type, do_transform: bool):
    be_mesh_obj = bpy.data.objects.new(js_obj["Name"], mesh)

    if do_transform:
        SetTransformFromJSON(js_obj, be_mesh_obj, engine_type)

    return be_mesh_obj


def SetTransformFromJSON(js_obj, be_obj, engine_type: str):
    be_obj.location = js_obj["Pos"]
    SetRotationFromJSON(be_obj, js_obj["Rot"], engine_type)
    be_obj.scale = js_obj["Scale"]


def RecordObjectOutputToJSON(inst_dict, the_object, is_instance: bool):

    if is_instance:
        the_mesh = the_object.object.data
        obj_type = the_object.object.type
        true_obj = the_object.object
    else:
        the_mesh = the_object.data
        obj_type = the_object.type
        true_obj = the_object

    if the_mesh not in inst_dict.keys():
        inst_dict[the_mesh] = {}
        inst_dict[the_mesh]["Transforms"] = []

    cur_inst_data = inst_dict[the_mesh]

    # Setup Transforms
    inst_pos, inst_rot, inst_scale = the_object.matrix_world.decompose()

    cur_inst_data["Transforms"].append((tuple(inst_pos), tuple(inst_rot.to_euler('XYZ')), tuple(inst_scale)))

    # Setup bengine_instance Value and Mesh
    if obj_type == "MESH":
        if BENGINE_INSTANCE in the_mesh.attributes.keys():
            if BENGINE_INSTANCE not in cur_inst_data.keys():
                if len(the_mesh.attributes[BENGINE_INSTANCE].data) > 0:
                    cur_inst_data["Bengine_Instance"] = the_mesh.attributes[BENGINE_INSTANCE].data[0].value
        else:
            if "Mesh" not in cur_inst_data.keys():
                # GET INSTANCE MESH
                cur_inst_data["Mesh"] = MeshToJSONData(true_obj)


def SaveBlenderOutputs(context, process_objs: list, be_paths: BEProjectPaths, engine_type: str, is_GN: bool):

    depsgraph = context.evaluated_depsgraph_get()

    # MAIN Data
    js_output_data = {}  # Output JSON Data
    inst_dict = {}  # Instances Dictionary
    meshes = []  # All Meshes
    
    # parse_objs = [process_objs]

    ev_objs = []

    # GET Evaluated Objects
    for obj in process_objs:
        if obj.name in depsgraph.objects.keys():
            ev_objs.append(depsgraph.objects[obj.name])
        elif obj.name in bpy.data.objects.keys():
            ev_objs.append(bpy.data.objects[obj.name])


    ev_objs_set = set(ev_objs)

    if is_GN:
        # GET MAIN MESH (FOR GN ONLY)!!!
        main_mesh_dict = MeshToJSONData(ev_objs[0])

        # If the main mesh has Verts/Polygons
        # Only one mesh at the moment
        if len(main_mesh_dict["Verts"]) > 0:
            # meshes.insert(0, main_mesh_dict)
            meshes.append(main_mesh_dict)  # Add mesh to a list

        if meshes:
            js_output_data["Meshes"] = meshes
    else:
        # GET SVERCHOK OBJECS AND MESHES
        for obj in ev_objs:
            RecordObjectOutputToJSON(inst_dict, obj, False)

    # GET INSTANCES
    for obj_instance in depsgraph.object_instances:
        if obj_instance.parent in ev_objs_set and obj_instance.is_instance:

            RecordObjectOutputToJSON(inst_dict, obj_instance, True)

    # Record Objects/Instances
    if inst_dict:
        js_output_data["Instances"] = list(inst_dict.values())

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

    # Get Normals
    if BENGINE_NORMAL in process_obj.data.attributes.keys():
        if process_obj.data.attributes[BENGINE_NORMAL].domain == 'CORNER':
            np_normals = np.zeros(len(process_obj.data.attributes[BENGINE_NORMAL].data) * 3, dtype=np.float32)
            process_obj.data.attributes[BENGINE_NORMAL].data.foreach_get('vector', np_normals)
            np_normals.shape = (len(process_obj.data.attributes[BENGINE_NORMAL].data), 3)
        else:
            print("Attribute " + BENGINE_NORMAL + " must have FACECORNER domain!!!")
            np_normals = GetMeshNormalsNumpy(process_obj)
    else:
        np_normals = GetMeshNormalsNumpy(process_obj)

    mesh_dict["Normals"] = np_normals.tolist()

    # GET UVS, Colors, Materials
    uvs_dict = {}
    np_col_attrib = None

    # Get Attributes
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
                print("Attribute " + attrib_name + " must have FACECORNER domain!!!")

        elif attrib_name == BENGINE_COLOR:

            if process_obj.data.attributes[attrib_name].domain == 'CORNER':
                # col_attrib = [tuple(uv_attr.color) for uv_attr in process_obj_ev.data.attributes[attrib_name].data]
                # mesh_dict["VertexColor"] = col_attrib

                np_col_attrib = np.zeros(len(process_obj.data.attributes[attrib_name].data) * 4, dtype=np.float32)
                process_obj.data.attributes[attrib_name].data.foreach_get('color', np_col_attrib)
                np_col_attrib.shape = (len(process_obj.data.attributes[attrib_name].data), 4)
                mesh_dict["VertexColors"] = np_col_attrib.tolist()
            else:
                print("Attribute " + attrib_name + " must have FACECORNER domain!!!")

        # Setup bengine_material Value
        elif attrib_name == BENGINE_MATERIAL:
            if process_obj.data.attributes[attrib_name].domain == 'FACE':
                np_mat_attrib = np.zeros(len(process_obj.data.attributes[attrib_name].data), dtype=np.uint8)
                process_obj.data.attributes[attrib_name].data.foreach_get('value', np_mat_attrib)
                mesh_dict["Materials"] = np_mat_attrib.tolist()
            else:
                print("Attribute " + attrib_name + " must have FACE domain!!!")

    if uvs_dict:
        mesh_dict["UVs"] = uvs_dict
    
    return mesh_dict


def GetMeshNormalsNumpy(process_obj):
    # Calc Split Nomrals
    process_obj.data.calc_normals_split()

    # GET NORMALS
    np_normals = np.zeros(len(process_obj.data.loops) * 3, dtype=np.float32)
    process_obj.data.loops.foreach_get("normal", np_normals)
    np_normals.shape = (len(process_obj.data.loops), 3)

    return np_normals


def SetRotationFromJSON(obj, js_euler, engine_type: str):
    if engine_type == "Unity":
        # Set Rotation
        rot_YXZ = Euler(js_euler, 'YXZ')
        rot_mat = rot_YXZ.to_matrix()
        rot_XYZ = rot_mat.to_euler('XYZ')

        obj.rotation_euler = rot_XYZ

    else:
        obj.rotation_euler = js_euler