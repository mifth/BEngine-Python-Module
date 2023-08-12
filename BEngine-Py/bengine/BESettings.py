from enum import Enum
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


class EngineType(Enum):
    Unity = 0
    Unreal = 1


class RunBlenderType(Enum):
    RunBlender = 0
    RunNetwork = 1


class RunNodesType(Enum):
    UpdateNodes = 0
    RunNodes = 1


# Sverchok Constants
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


class BaseStuff:
    section = "/NodeTree/"
    blendfile = ""
    blendfolder = ""
    node_sys_name = ""

    blendfile_basename = ""
    blendfile_name = ""

    filepath = ""
    directory = ""
    filename = ""

    engine_type: EngineType

    def __init__(self, be_paths: dict):
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

        self.engine_type = EngineType[be_paths["BEngineType"]]

        #  Run Nodes Type
        self.run_type = be_paths["RunNodesType"]
        if RunNodesType.RunNodes._name_ == self.run_type:
            self.run_type = RunNodesType.RunNodes
        else:
            self.run_type = RunNodesType.UpdateNodes


