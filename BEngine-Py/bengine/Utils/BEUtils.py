import os
import stat
import bpy

import json
from json.decoder import JSONDecodeError

# import numpy as np
# from math import degrees

from mathutils import Color, Vector, Euler

from .. import BESettings
from ..BESettings import BaseStuff, EngineType
# from ..BEStartParams import StartParams

from . import BEUtilsGeo
from . import BEGNInputs


def LoadJSON(bengineInputs_path: str):
    with open(bengineInputs_path) as js_file:
        try:
            js_input_data = json.load(js_file)
        except JSONDecodeError:
            print("Problem to Open File: " + bengineInputs_path)
            js_input_data = None

    return js_input_data


def SaveJSON(gn_js_path, js_data):

    # Set Writable
    if os.path.exists(gn_js_path) and not os.access(gn_js_path, os.W_OK):
        os.chmod(gn_js_path, stat.S_IWRITE)
        print("File Was Read-Only and Has Been Changed: " + gn_js_path)

    # Save JSON
    with open(gn_js_path, 'w') as json_file:
        json.dump(js_data, json_file)


# Set GN/SV Default/Min/Max Values
# input is either GNNodeInputs or SVNode
def SetBaseInputValues(input_data, input, is_GN: bool):
    input_obj = input

    # If Blen 3
    if bpy.app.version[0] == 3:
        if is_GN:
            input_obj = input[1]


    match input_data['Type']:
        case 'VALUE':
            if is_GN:
                input_data['DefaultValue'] = input_obj.default_value
                # input_data['DefaultValue'] = numpy.float32(input_obj.default_value)

                input_data['MinValue'] = input_obj.min_value
                input_data['MaxValue'] = input_obj.max_value

                # input_data['Value'] = geom_mod[input_obj.identifier]
            else:
                input_data['DefaultValue'] = input_obj['BEFloatDefault']
                input_data['MinValue'] = input_obj['BEFloatMin']
                input_data['MaxValue'] = input_obj['BEFloatMax']

        case 'INT':
            if is_GN:
                input_data['DefaultValue'] = input_obj.default_value
                input_data['MinValue'] = input_obj.min_value
                input_data['MaxValue'] = input_obj.max_value
            else:
                input_data['DefaultValue'] = input_obj['BEIntegerDefault']
                input_data['MinValue'] = input_obj['BEIntegerMin']
                input_data['MaxValue'] = input_obj['BEIntegerMax']

        case 'BOOLEAN':
            if is_GN:
                input_data['DefaultValue'] = input_obj.default_value
            else:
                input_data['DefaultValue'] = input_obj['BEBooleanDefault']

        case 'STRING':
            if is_GN:
                input_data['DefaultValue'] = input_obj.default_value
            else:
                input_data['DefaultValue'] = input_obj['BEStringDefault']

        case 'RGBA':
            if is_GN:
                input_data['DefaultValue'] = list(input_obj.default_value)
            else:
                input_data['DefaultValue'] = list(input_obj['BEColorDefault'])

        case 'VECTOR':
            if is_GN:
                input_data['DefaultValue'] = list(input_obj.default_value)
                input_data['MinValue'] = input_obj.min_value
                input_data['MaxValue'] = input_obj.max_value
            else:
                input_data['DefaultValue'] = list(input_obj['BEVectorDefault'])
                input_data['DefaultValue'] = input_obj['BEVectorMin']
                input_data['DefaultValue'] = input_obj['BEVectorMax']


def GetSVOutputObjects(node_tree):
    sv_out_nodes = []
    sv_out_objs = []

    for node in node_tree.nodes:
        if node.bl_idname == BESettings.TYPE_SV_SCRIPT:
            if BESettings.SVConstants.SV_OUTPUT_OBJ in node.script_name:
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
        if node.bl_idname == BESettings.TYPE_SV_SCRIPT:
            for in_out_name in BESettings.SVConstants.SV_Inputs:
                if in_out_name in node.script_name:
                    the_name = ''

                    # Set Type
                    match in_out_name:
                        case BESettings.SVConstants.SV_INPUT_BOOL:
                            the_name = 'BOOLEAN'
                        case BESettings.SVConstants.SV_INPUT_COLL:
                            the_name = 'COLLECTION'
                        case BESettings.SVConstants.SV_INPUT_COLOR:
                            the_name = 'RGBA'
                        case BESettings.SVConstants.SV_INPUT_FLOAT:
                            the_name = 'VALUE'
                        case BESettings.SVConstants.SV_INPUT_INT:
                            the_name = 'INT'
                        case BESettings.SVConstants.SV_INPUT_OBJ:
                            the_name = 'OBJECT'
                        case BESettings.SVConstants.SV_INPUT_STR:
                            the_name = 'STRING'
                        case BESettings.SVConstants.SV_INPUT_VEC:
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

    for input in BEGNInputs.GetNodeTreeInputs(node_group):
        input_data = {}
        input_data['Type'] = BEGNInputs.GetInputType(input)
        input_data['Name'] = BEGNInputs.GetInputName(input)
        input_data['Identifier'] = BEGNInputs.GetInputIdentifier(input)

        # Set Default/Min/Max Values
        SetBaseInputValues(input_data, input, True)

        gn_inputs_data.append(input_data)

    return gn_inputs_data


def LoadNodesTreeFromJSON(context, be_base_stuff: BaseStuff):

    bpy.ops.wm.link(filepath=be_base_stuff.filepath, filename=be_base_stuff.filename,
                    directory=be_base_stuff.directory, link=False)

    if (bpy.data.node_groups):
        node_tree = bpy.data.node_groups[be_base_stuff.node_sys_name]

        process_gn_obj = None
        geom_mod = None

        # If GN NodeTree
        if node_tree.bl_idname == BESettings.TYPE_GN:
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
                        engine_type: EngineType):

    if "BEngineInputs" in js_input_data:
        js_inputs = js_input_data["BEngineInputs"]

        is_GN = node_tree.bl_idname == BESettings.TYPE_GN

        coll_idx = 0

        # GN - Inputs
        # SV - SVInputNodes
        if is_GN:
            input_items = BEGNInputs.GetNodeTreeInputs(node_tree)
        else:
            input_items = GetSVInputNodes(node_tree)

        instanced_meshes = {}

        for input in input_items:

            if is_GN:
                node_id = BEGNInputs.GetInputIdentifier(input)
            else:
                node_id = input[1].node_id

            # NEED TO DO THE SAME FOR SVERCHOK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            input_name = BEGNInputs.GetInputName(input)
            input_type = BEGNInputs.GetInputType(input)

            if node_id in js_inputs.keys():

                # Check if the same type
                if is_GN:
                    is_same_type = (input_type == js_inputs[node_id]["Type"])

                    if not is_same_type:
                        print("!Input " + input_name + " is not the same type! " + input_type + " " + js_inputs[node_id]["Type"])
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
                                GN_mod[node_id][0] = js_prop["Value"][0]
                                GN_mod[node_id][1] = js_prop["Value"][1]
                                GN_mod[node_id][2] = js_prop["Value"][2]
                                GN_mod[node_id][3] = js_prop["Value"][3]
                            else:
                                input[1]['BEColor'][0] = js_prop["Value"][0]
                                input[1]['BEColor'][1] = js_prop["Value"][1]
                                input[1]['BEColor'][2] = js_prop["Value"][2]
                                input[1]['BEColor'][3] = js_prop["Value"][3]

                        case "VECTOR":
                            if is_GN:
                                GN_mod[node_id][0] = js_prop["Value"][0]
                                GN_mod[node_id][1] = js_prop["Value"][1]
                                GN_mod[node_id][2] = js_prop["Value"][2]
                            else:
                                input[1]['BEVector'][0] = js_prop["Value"][0]
                                input[1]['BEVector'][1] = js_prop["Value"][1]
                                input[1]['BEVector'][2] = js_prop["Value"][2]

                        case "IMAGE":
                            new_img = bpy.data.images.load(js_prop["Value"])

                            if is_GN:
                                GN_mod[node_id] = new_img

                        # case "TEXTURE":
                        #     pass

                        case "MATERIAL":
                            mat = bpy.data.materials.new(name="BEMaterial")

                            if is_GN:
                                GN_mod[node_id] = mat

                        case "OBJECT":
                            js_obj_val = js_prop["Value"]

                            be_objs, has_mesh = ParseObjectFromJSON(js_obj_val,
                                                                    js_input_data, instanced_meshes,
                                                                    engine_type, False, True)

                            # Join Meshes
                            be_obj = None
                            
                            if len(be_objs) > 1:
                                bpy.ops.object.select_all(action='DESELECT')
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
                                GN_mod[node_id] = be_obj
                            else:
                                input[1]['BEObject'] = be_obj.name

                        case "COLLECTION":
                            js_coll_val = js_prop["Value"]

                            be_coll = bpy.data.collections.new('BEngine_' + str(coll_idx))
                            context.scene.collection.children.link(be_coll)

                            be_coll_objs, has_mesh = ParseObjectFromJSON(js_coll_val,
                                                                        js_input_data, instanced_meshes,
                                                                        engine_type, True, False)

                            for obj in be_coll_objs:
                                be_coll.objects.link(obj)

                            if is_GN:
                                GN_mod[node_id] = be_coll
                            else:
                                input[1]['BECollection'] = be_coll.name

                            coll_idx += 1

                        case "VALUE":
                            if is_GN:
                                GN_mod[node_id] = float(js_prop["Value"])
                            else:
                                input[1]['BEFloat'] = float(js_prop["Value"])

                        case "INT":
                            if is_GN:
                                GN_mod[node_id] = js_prop["Value"]
                            else:
                                input[1]['BEInteger'] = js_prop["Value"]

                        case "STRING":
                            if is_GN:
                                GN_mod[node_id] = js_prop["Value"]
                            else:
                                input[1]['BEString'] = js_prop["Value"]

                        case "BOOLEAN":
                            if is_GN:
                                GN_mod[node_id] = js_prop["Value"]
                            else:
                                input[1]['BEBoolean'] = js_prop["Value"]

                        case default:
                            if is_GN:
                                GN_mod[node_id] = js_prop["Value"]

                    # else:
                    #     GN_mod[node_id] = prop_value


def ParseObjectFromJSON(js_obj_val, js_input_data, instanced_meshes,
                        engine_type: EngineType, isCollection: bool,
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
                be_mesh = BEUtilsGeo.MeshFromJSON(js_mesh, engine_type)

                instanced_meshes[js_obj["Mesh"]] = be_mesh
            else:
                be_mesh = instanced_meshes[js_obj["Mesh"]]

            be_mesh_obj = ObjectFromJSON(js_obj, be_mesh, engine_type, True)

            be_objs.append(be_mesh_obj)

        # Import Curves
        if "Curves" in js_obj:
            if (convert_to_meshes):
                be_curves_data = BEUtilsGeo.CurvesFromJSON(js_obj, engine_type, bool(1 - has_mesh))
            else:
                be_curves_data = BEUtilsGeo.CurvesFromJSON(js_obj, engine_type, True)

            be_curves_obj = ObjectFromJSON(js_obj, be_curves_data, engine_type, True)

            be_objs.append(be_curves_obj)

        # Import Terrain
        if "Terrain" in js_obj:
            be_terr_mesh = BEUtilsGeo.TerrainMeshFromJSON(js_obj, engine_type)
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
                    be_append_obj = None

                    if len(js_obj_val) > 1:
                        if has_mesh:
                            empty_mesh_data = BEUtilsGeo.CreateEmptyMesh()

                            be_append_obj = bpy.data.objects.new(js_obj["Name"], empty_mesh_data)
                        else:
                            empty_curv_data = bpy.data.curves.new(js_obj["Name"], type='CURVE')
                            empty_curv_data.dimensions = '3D'

                            be_append_obj = bpy.data.objects.new(js_obj["Name"], empty_curv_data)

                    else:
                        # Empty
                        be_append_obj = bpy.data.objects.new(js_obj["Name"], None )

                    SetTransformFromJSON(js_obj, be_append_obj, engine_type)

                    be_objs.append(be_append_obj)

    instanced_meshes = None  # Clear Meshes

    return be_objs, has_mesh


def ObjectFromJSON(js_obj, mesh, engine_type, do_transform: bool):
    be_mesh_obj = bpy.data.objects.new(js_obj["Name"], mesh)

    if do_transform:
        SetTransformFromJSON(js_obj, be_mesh_obj, engine_type)

    return be_mesh_obj


def SetTransformFromJSON(js_obj, be_obj, engine_type: EngineType):
    be_obj.location = js_obj["Pos"]
    SetRotationFromJSON(be_obj, js_obj["Rot"], engine_type)
    be_obj.scale = js_obj["Scale"]


def RecordObjectOutputToJSON(objects_sets_dict, the_object, is_instance: bool,
                             js_meshes: list, meshes_tmp_list: list, 
                             meshes_tmp_set: set, engine_type: EngineType):

    if is_instance:
        mesh = the_object.object.data
        obj_type = the_object.object.type
        true_obj = the_object.object
    else:
        mesh = the_object.data
        obj_type = the_object.type
        true_obj = the_object

    # Add Default Keys
    if mesh not in objects_sets_dict.keys():
        objects_sets_dict[mesh] = {}
        objects_sets_dict[mesh]["Transforms"] = []

    js_object_data = objects_sets_dict[mesh]

    # Setup Transforms
    inst_pos, inst_rot, inst_scale = the_object.matrix_world.decompose()
    js_object_data["Transforms"].append((tuple(inst_pos), tuple(inst_rot.to_euler('XYZ')), tuple(inst_scale)))

    # Get Mesh or BENGINE_INSTANCE
    if obj_type == "MESH":
        # Get BENGINE_INSTANCE Value
        if BESettings.BENGINE_INSTANCE in mesh.attributes.keys():
            if BESettings.BENGINE_INSTANCE not in js_object_data.keys():
                if len(mesh.attributes[BESettings.BENGINE_INSTANCE].data) > 0:

                    be_inst_id = mesh.attributes[BESettings.BENGINE_INSTANCE].data[0].value

                    if type(be_inst_id) is int:
                        js_object_data["BE_Instance"] = be_inst_id
                    else:
                        print(BESettings.BENGINE_INSTANCE + " Attribute is not Integer!!!")

        # Get Mesh to JSON
        elif "Mesh" not in js_object_data.keys():
            if mesh not in meshes_tmp_set:
                js_mesh = BEUtilsGeo.MeshToJSONData(mesh, engine_type)
                js_meshes.append(js_mesh)

                js_object_data["Mesh"] = len(meshes_tmp_list)

                meshes_tmp_list.append(mesh)
                meshes_tmp_set.add(mesh)

            else:
                js_object_data["Mesh"] = meshes_tmp_list.index(mesh)


def GetBlenderOutputs(context, process_objs: list, engine_type: EngineType, is_GN: bool):

    depsgraph = context.evaluated_depsgraph_get()

    # MAIN Data
    js_output_data = {}  # Output JSON Data
    objects_sets_dict = {}  # Instances Dictionary

    meshes_tmp_list = []
    meshes_tmp_set = set()
    js_meshes_list = []  # All Parsed JSON Meshes

    process_ev_objs = [depsgraph.objects[obj.name] for obj in process_objs]
    process_ev_objs_set = set(process_ev_objs)

    # # GET MAIN MESH
    # if is_GN:
    #     # GET MAIN MESH (FOR GN ONLY)!!!
    #     main_mesh_dict = BEUtilsGeo.MeshToJSONData(process_objs[0])

    #     # If the main mesh has Verts/Polygons
    #     # Only one mesh at the moment
    #     if len(main_mesh_dict["Verts"]) > 0:
    #         # meshes.insert(0, main_mesh_dict)
    #         meshes.append(main_mesh_dict)  # Add mesh to a list

    #     if meshes:
    #         js_output_data["Meshes"] = meshes
    # else:

    # GET OBJECS AND MESHES
    for obj in process_ev_objs:
        # If GeometryNodes main mesh has no points/polygons
        if is_GN and len(obj.data.vertices) == 0:
            continue

        RecordObjectOutputToJSON(objects_sets_dict, obj, False,
                                 js_meshes_list, meshes_tmp_list,
                                 meshes_tmp_set, engine_type)

    # GET INSTANCES
    for obj_instance in depsgraph.object_instances:
        if obj_instance.parent in process_ev_objs_set and obj_instance.is_instance:
            RecordObjectOutputToJSON(objects_sets_dict, obj_instance, True,
                                     js_meshes_list, meshes_tmp_list,
                                     meshes_tmp_set, engine_type)

    # Record Objects/Instances
    if objects_sets_dict:
        js_output_data["ObjectsSets"] = list(objects_sets_dict.values())
    else:
        js_output_data["ObjectsSets"] = []

    # Record Meshes
    js_output_data["Meshes"] = js_meshes_list

    # gn_js_path = be_paths.be_tmp_folder + BESettings.OUTPUT_JSON_NAME
    # SaveJSON(gn_js_path, js_output_data)

    return js_output_data


def SetRotationFromJSON(obj, js_euler, engine_type: EngineType):
    if engine_type == EngineType.Unity:
        # Set Rotation
        rot_YXZ = Euler(js_euler, 'YXZ')
        rot_mat = rot_YXZ.to_matrix()
        rot_XYZ = rot_mat.to_euler('XYZ')

        obj.rotation_euler = rot_XYZ

    else:
        obj.rotation_euler = Euler(js_euler, 'XYZ')


