from enum import Enum
import sys
import os


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


class RunBlenderType(Enum):
    RunBlender = 1
    RunNetwork = 2


class RunNodesType(Enum):
    UpdateNodes = 1
    RunNodes = 2


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


class StartParams:

    def __init__(self):
        self.be_tmp_folder = None
        self.project_path = None
        self.project_path_2 = None

        self.run_blender_Type = None
        self.host = None
        self.port = None
        self.buffer_size = None

        args = sys.argv

        for arg in args:
            if arg.startswith('BE_TMP_FOLDER='):
                self.be_tmp_folder = arg.replace('BE_TMP_FOLDER=', '')
            elif arg.startswith('PROJECT_PATH='):
                self.project_path = arg.replace('PROJECT_PATH=', '')
            elif arg.startswith('PROJECT_PATH_2='):
                self.project_path_2 = arg.replace('PROJECT_PATH_2=', '')

        # Networking
            elif arg.startswith('RunBlenderType='):
                self.run_blender_type = arg.replace('RunBlenderType=', '')

                if RunBlenderType.RunBlender._name_ == self.run_blender_type:
                    self.run_blender_type = RunBlenderType.RunBlender
                else:
                    self.run_blender_type = RunBlenderType.RunNetwork

            elif arg.startswith('Host='):
                self.host = arg.replace('Host=', '')
            elif arg.startswith('Port='):
                self.port = int(arg.replace('Port=', ''))
            elif arg.startswith('MaxPackageBytes='):
                self.buffer_size = int(arg.replace('MaxPackageBytes=', ''))


START_PARAMS = StartParams()


class BaseStuff:

    def __init__(self, be_paths: dict):
        self.section = "/NodeTree/"
        self.blendfile = ""
        self.blendfolder = ""
        self.node_sys_name = ""

        self.blendfile = be_paths["BlendFile"]

        self.blendfolder = be_paths["BlendFolder"]
        if not self.blendfolder.endswith('/'):
            self.blendfolder = self.blendfolder + "/"

        self.node_sys_name = be_paths["NodeSysName"]

        # blend file name
        self.blendfile_basename = os.path.basename(self.blendfile)
        self.blendfile_name = os.path.splitext(self.blendfile_basename)[0]

        # Load GN Paths
        self.filepath = self.blendfile + self.section + self.node_sys_name
        self.directory = self.blendfile + self.section
        self.filename = self.node_sys_name

        self.be_type = be_paths["BEngineType"]

        #  Run Nodes Type
        self.run_type = be_paths["RunNodesType"]
        if RunNodesType.RunNodes._name_ == self.run_type:
            self.run_type = RunNodesType.RunNodes
        else:
            self.run_type = RunNodesType.UpdateNodes

        # # Networking
        # self.RunBlenderType = be_paths["RunBlenderType"]
        # self.Host = be_paths["Host"]
        # self.Port = be_paths["Port"]
        # self.MaxPackageBytes = be_paths["MaxPackageBytes"]


