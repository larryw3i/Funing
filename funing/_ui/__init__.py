

import os
import shutil
import sys
import uuid

import cv2
import yaml

from funing import settings
from funing._ui import error

error.lib_check()


class Enjoy():
    def __init__(self):
        if not settings.initialized:
            self.initialize()

    def start(self):
        from ._main_ui import _MainUI
        _MainUI()

    def initialize(self):

        for d in [settings.faces_path, settings.infos_path]:
            if not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

        settings.config_yml["version"] = settings.version
        settings.config_yml["initialized"] = True
        yaml.safe_dump(settings.config_yml,
                       open(settings._config_path, 'w'))

    def keep_code(self):
        rm_dirs = [
            settings._config_path,
            settings.data_dir
        ]

        uuid_cp_path = os.path.join(settings.backup_dir_path,
                                    str(uuid.uuid4()))

        if not os.path.exists(uuid_cp_path):
            os.makedirs(uuid_cp_path, exist_ok=True)

        for root, dirs, files in os.walk(settings.project_path):
            for f in files:
                if f.endswith('.mo'):
                    os.rename(
                        os.path.join(
                            root, f), os.path.join(
                            uuid_cp_path, f'{str(uuid.uuid4())}--{f}'))

        for _cp in rm_dirs:
            shutil.move(_cp, uuid_cp_path)
