import os
import os.path
import json
from os import walk, makedirs, remove
import re
from codecs import open
from os.path import join, dirname, exists, relpath, abspath, basename, isfile
from sys import platform
from json_tools import prepare, field_by_path, list_field_paths
from utils import get_answer
import yaml

from patch_tool import trans_patch
if platform == "win32":
    from os.path import normpath as normpath_old


def import_patch(patch_dir, file_dir):
    for path, d, filelist in os.walk(file_dir):
        for thefile in filelist:
            if thefile in ["substitutions.yml", "totallabels.yml", "translatedlabels.yml", "patch_substitutions.yml", "parse_problem.txt"]:
                continue
            if thefile.endswith(".yml"):
                yml_file = join(path, thefile)
                with open(yml_file, "rb+", "utf-8") as f:
                    yaml_dict = yaml.safe_load(f)
                    print(basename(yml_file))
                for i, v in enumerate(yaml_dict):
                    for w in yaml_dict[i]['Files'].keys():
                        patch_file = join(patch_dir, w)+".patch"
                        try:
                            patch_data = json.load(
                                open(patch_file, "rb+", "utf-8"))
                        except:
                            continue
                        for y, z in enumerate(patch_data):
                            if yaml_dict[i]['Files'][w][0] == patch_data[y]["path"]:
                                yaml_dict[i]['Texts']['Chs'] = patch_data[y]["value"]
                f = open(yml_file, "rb+", "utf-8")
                yaml.dump(
                    yaml_dict, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)


if __name__ == "__main__":
    patch_dir_1 = "E:/SteamLibrary/steamapps/workshop/content/211820/1929019607/RPG_Growth_Chinese_Reborn"
    file_dir_1 = "F:/Starbound-RPG-Growth-Chinese/translations/texts"
    import_patch(patch_dir_1, file_dir_1)
