import bpy

# from unicodedata import decimal

# try:
#     from .Utils import BEUtils
# except:
#     # Load BEUtils
#     PACKAGE_PARENT = pathlib.Path(__file__).parent
#     #PACKAGE_PARENT = pathlib.Path.cwd().parent # if on jupyter notebook
#     SCRIPT_DIR = PACKAGE_PARENT
#     sys.path.append(str(SCRIPT_DIR) + "/Utils")

#     import BEUtils

from .Utils import BEUtils
from . import BESettings
from .BEStartParams import StartParams


def Run():

    # BEUtils.ClearScene()
    bpy.ops.wm.read_homefile(use_empty=True)
    # bpy.ops.wm.read_factory_settings(use_empty=True)

    window = bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=window):

        context = bpy.context

        start_params = StartParams()

        # Base Stuff
        beBaseStuff_path = start_params.be_tmp_folder + "BEngineBaseFromEngine.json"
        js_base_stuff = BEUtils.LoadJSON(beBaseStuff_path)

        be_base_stuff = BEUtils.BaseStuff(js_base_stuff)

        process_gn_obj, geom_mod, node_tree = BEUtils.LoadNodesTreeFromJSON(context, be_base_stuff)

        if node_tree:

            if be_base_stuff.run_type == BESettings.RunNodesType.UpdateNodes:
                SaveBlenderInputs(be_base_stuff, node_tree)
            else:
                # GET BLENDER INPUTS
                beInputs_path = start_params.be_tmp_folder + "BEngineInputs.json"
                js_input_data = BEUtils.LoadJSON(beInputs_path)

                js_output_data = RunNodes(context, js_input_data, node_tree,
                                        process_gn_obj, geom_mod, be_base_stuff)
                
                # Save Outputs
                if js_output_data:
                    gn_js_path = start_params.be_tmp_folder + BESettings.OUTPUT_JSON_NAME
                    BEUtils.SaveJSON(gn_js_path, js_output_data)

            print("!PYTHON DONE!")  # PYTHON IS DONE

            return True

        else:
            print("Nodes were not Loaded! Please check Paths and NodeTree Name!")
            return False


def MakeInputsJS(node_tree):
    # ORIGINAL STUFF
    # Get GN Data
    js_output_data = {}

    if node_tree.bl_idname == BESettings.TYPE_SV:
        gn_inputs_data = BEUtils.GetSVInputsData(node_tree)
    else:
        gn_inputs_data = BEUtils.GetGNInputsData(node_tree)

    js_output_data['Inputs'] = gn_inputs_data

    return js_output_data


def SaveBlenderInputs(be_base_stuff: BEUtils.BaseStuff, node_tree):
    js_output_data = MakeInputsJS(node_tree)

    gn_js_path = be_base_stuff.blendfolder + be_base_stuff.blendfile_name + '_' + be_base_stuff.node_sys_name + '.json'

    print("JSON Path to Save: " + gn_js_path)

    BEUtils.SaveJSON(gn_js_path, js_output_data)


def RunNodes(context, js_inputs, node_tree, process_gn_obj, geom_mod, be_base_stuff):
    if js_inputs:
        # If GN
        if node_tree.bl_idname == BESettings.TYPE_GN and process_gn_obj:
            # Set Transform
            process_gn_obj.location = js_inputs["Pos"]
            BEUtils.SetRotationFromJSON(process_gn_obj, js_inputs["Rot"], be_base_stuff.engine_type)
            process_gn_obj.scale = js_inputs["Scale"]

            # Setup inputs
            BEUtils.SetupInputsFromJSON(context, node_tree, geom_mod,
                                        js_inputs, be_base_stuff.engine_type)
            # geom_mod.show_viewport = True

            # Set the GN Object Active and Selected
            bpy.ops.object.select_all(action='DESELECT')
            process_gn_obj.select_set(True)
            context.view_layer.objects.active = process_gn_obj

            process_gn_obj.data.update()

            js_output_data = BEUtils.GetBlenderOutputs(context, [process_gn_obj], be_base_stuff.engine_type, True)
            return js_output_data

        # If SV
        elif node_tree.bl_idname == BESettings.TYPE_SV:
            # node_tree = node_tree.evaluated_get(context.evaluated_depsgraph_get())

            # Setup inputs
            BEUtils.SetupInputsFromJSON(context, node_tree, None,
                                        js_inputs, be_base_stuff.engine_type)

            # Update All Nodes
            # node_tree.update()
            context.view_layer.update()
            node_tree.process_ani(True, False)

            js_output_data = BEUtils.GetBlenderOutputs(context, BEUtils.GetSVOutputObjects(node_tree), 
                                                        be_base_stuff.engine_type, False)
            return js_output_data

        else:
            print("Nodes were not Loaded! Please check Paths and NodeTree Name!")
            return None
    else:
        print("JSON Object is Empty!!!")
        return None

    return None
