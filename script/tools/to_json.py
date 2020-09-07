import yaml
import json
from json_tools import prepare
from codecs import open
from os import walk, makedirs, remove
from os.path import join, dirname, exists, relpath, abspath, basename
from sys import platform
if platform == "win32":
    from os.path import normpath as normpath_old
old_dir = "F:/Starbound-RPG-Growth-Chinese/translations"
for path,d,filelist in walk(old_dir):
        for filename in filelist:
            if filename.endswith(".yml"):
                i = join(path,filename).replace("\\","/")
                with open(i, "r",  "utf-8") as f:
                    yml = yaml.load(f, Loader=yaml.FullLoader)
                new_file = open(i.replace(".yml",".json"), "w",  "utf-8")
                json.dump(yml,new_file,ensure_ascii=False, indent=2, sort_keys=True)
                remove(i)
"""
test_json_file = "F:/FFS-sChinese-Project/translations/texts/ffs_weapons/ffs_5_at/ffs_at4/ffs_at4_1.activeitem.yml"
test_file = open(test_json_file,"r", "utf_8_sig")
test_json = yaml.load(test_file, Loader=yaml.FullLoader)
test_dict = test_json
test_yaml = yaml.dump(test_dict,default_flow_style=False, encoding='utf-8',
                  allow_unicode=True, indent=4)
print(test_json)
print(test_yaml)
"""