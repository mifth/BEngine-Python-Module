import sys
from .BESettings import RunBlenderType


class StartParams:

    def __init__(self):
        self.be_tmp_folder: str = None

        self.run_blender_Type: RunBlenderType = None
        self.host: str = None
        self.port: int = None
        self.buffer_size: int = None

        args = sys.argv

        for arg in args:
            if arg.startswith('BE_TMP_FOLDER='):
                self.be_tmp_folder = arg.replace('BE_TMP_FOLDER=', '')
            # elif arg.startswith('PROJECT_PATH='):
            #     self.project_path = arg.replace('PROJECT_PATH=', '')
            # elif arg.startswith('PROJECT_PATH_2='):
            #     self.project_path_2 = arg.replace('PROJECT_PATH_2=', '')

            # Networking
            elif arg.startswith('RunBlenderType='):
                arg_run_blender_type = arg.replace('RunBlenderType=', '')

                if arg_run_blender_type == RunBlenderType.RunBlender.name:
                    self.run_blender_type = RunBlenderType.RunBlender
                else:
                    self.run_blender_type = RunBlenderType.RunNetwork

            elif arg.startswith('Host='):
                self.host = arg.replace('Host=', '')
            elif arg.startswith('Port='):
                self.port = int(arg.replace('Port=', ''))
            elif arg.startswith('MaxPackageBytes='):
                self.buffer_size = int(arg.replace('MaxPackageBytes=', ''))