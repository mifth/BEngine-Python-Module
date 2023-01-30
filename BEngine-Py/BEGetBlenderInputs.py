# Main Stuff
try:

    import bpy

    import traceback
    # from unicodedata import decimal

    import sys
    import os

    # import json
    # from json.decoder import JSONDecodeError

    # import numpy

    import time

    import pathlib

    try:
        from .Utils import BEUtils
    except:
        # Load BEUtils
        PACKAGE_PARENT = pathlib.Path(__file__).parent
        #PACKAGE_PARENT = pathlib.Path.cwd().parent # if on jupyter notebook
        SCRIPT_DIR = PACKAGE_PARENT
        sys.path.append(str(SCRIPT_DIR) + "/Utils")

        import BEUtils


    def MainWork():
        context = bpy.context

        BEUtils.ClearScene()

        be_proj_paths = BEUtils.BEProjectPaths()

        # Base Stuff
        beBaseStuff_path = be_proj_paths.be_tmp_folder + "BEngineBaseFromEngine.json"
        js_base_stuff = BEUtils.LoadJSON(beBaseStuff_path)

        be_base_stuff = BEUtils.BEBaseStuff(js_base_stuff)

        process_obj, geom_mod, node_tree = BEUtils.LoadNodesTreeFromJSON(context, be_proj_paths, be_base_stuff)

        if node_tree:

            # ORIGINAL STUFF
            # Get GN Data
            js_output_data = {}

            if node_tree.bl_idname == BEUtils.TYPE_SV:
                gn_inputs_data = BEUtils.GetSVInputsData(node_tree)
            else:
                gn_inputs_data = BEUtils.GetGNInputsData(node_tree)

            js_output_data['Inputs'] = gn_inputs_data

            # If No JSON File
            gn_js_path = be_base_stuff.blendfolder + be_base_stuff.blendfile_name + '_' + be_base_stuff.node_sys_name + '.json'
            BEUtils.SaveJSON(gn_js_path, js_output_data)

            return True

        else:
            print("Geometry Nodes were not Loaded! Please check Paths!")
            return False


    # start = time.time()

    is_done = MainWork()

    # end = time.time()
    # print(end - start)

    if is_done:
        print("!PYTHON DONE!")
    else:
        print("!PYTHON ERROR!")

except Exception as e:
    print(traceback.format_exc())
