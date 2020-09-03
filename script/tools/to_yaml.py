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
            if filename.endswith(".json"):
                i = join(path,filename).replace("\\","/")
                with open(i, "r",  "utf_8_sig") as f:
                    jsons = json.load(f)
                new_file = open(i.replace(".json",".yml"), "w",  "utf_8_sig")
                yaml.safe_dump(jsons,stream=new_file,default_flow_style=False,encoding='utf-8',allow_unicode=True)
                remove(i)
"""
test_json_file = "F:/Starbound-RPG-Growth-Chinese/translations/texts/glitchEmotes.json"
test_file = prepare(open(test_json_file,"r", "utf_8_sig"))
test_json = json.loads(test_file)
test_dict = test_json
test_yaml = yaml.dump(test_dict)
print(test_yaml)
"""
