import pathlib
import sys
import traceback

# Add the lib to path
PACKAGE_PARENT = pathlib.Path(__file__).parent
#PACKAGE_PARENT = pathlib.Path.cwd().parent # if on jupyter notebook
SCRIPT_DIR = PACKAGE_PARENT

sys.path.append(str(SCRIPT_DIR))


from bengine import BERunNodes, BENetworking, BESettings, BEStartParams


if BEStartParams.StartParams().run_blender_type == BEStartParams.RunBlenderType.RunNetwork:
    BENetworking.RunServer()
else:
    try:
        # start = time.time()

        BERunNodes.Run()

        # end = time.time()
        # print(end - start)

    except Exception as e:
        print("!PYTHON EXCEPTION!")
        print(traceback.format_exc())
