try:

    import bpy

    import traceback
    # from unicodedata import decimal

    import sys
    import os

    import json
    from json.decoder import JSONDecodeError

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


    def IsInstanceFromSelected(object_instance):
        # For instanced objects we check selection of their instancer (more accurately: check
        # selection status of the original object corresponding to the instancer).
        if object_instance.parent:
            return object_instance.parent.original.select_get()
        # For non-instanced objects we check selection state of the original object.
        return object_instance.object.original.select_get()


    def MainWork():
        context = bpy.context

        BEUtils.ClearScene()

        be_paths = BEUtils.BEPaths()

        process_obj, geom_mod, bengine_GN = BEUtils.LoadGN(context, be_paths)

        if (process_obj and bengine_GN):

            # ORIGINAL STUFF
            with open(be_paths.be_tmp_folder + "BEngineInputs.json") as js_file:
                try:
                    js_input_data = json.load(js_file)
                except JSONDecodeError:
                    js_input_data = {}

            engine_type = js_input_data["BEngineType"]

            # Set Transform
            process_obj.location = js_input_data["Pos"]
            BEUtils.SetRotationFromJSON(process_obj, js_input_data["Rot"], engine_type)
            process_obj.scale = js_input_data["Scale"]

            # Setup inputs
            BEUtils.SetupInputsFromJSON(context, bengine_GN, geom_mod,
                                        js_input_data["BEngineInputs"], be_paths, engine_type)
            # geom_mod.show_viewport = True

            # Set the GN Object Active and Selected
            bpy.ops.object.select_all(action='DESELECT')
            process_obj.select_set(True)
            context.view_layer.objects.active = process_obj

            process_obj.data.update()

            # Save Node Outputs
            BEUtils.SaveBlenderOutputs(context, process_obj, be_paths, engine_type)

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
