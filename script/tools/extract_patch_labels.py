#!/usr/bin/python3

from bisect import insort_left
from codecs import open as open_n_decode
from json import dump, load, loads
from multiprocessing import Pool
from os import makedirs, remove, walk
from os.path import abspath, basename, dirname, exists, join, relpath
from re import compile as regex
from sys import platform

from patch_tool import trans_patch, to_a_list
from ignore_file import ignore_filelist, ignore_filelist_patch
from patch_spciallist import patchfile_spciallist1, patchfile_spciallist2
from parser_settings import files_of_interest
from shared_path import getSharedPath
from special_cases import specialSections
from utils import get_answer

if platform == "win32":
    from os.path import normpath as normpath_old

    def normpath(path):
        return normpath_old(path).replace('\\', '/')
else:
    from os.path import normpath

root_dir = "F:/Starbound-RPG-Growth"
prefix = "F:/Starbound-RPG-Growth-Chinese/translations"
texts_prefix = "patches"
sub_file = normpath(join(prefix, "patch_substitutions.json"))
pro_list = normpath(join(prefix, "patch_problem.txt"))

glitchEmoteExtractor = regex("^([In]{,3}\s?[A-Za-z-]+\.)\s+(.*)")
glitchIsHere = regex("^.*[gG]litch.*")


def defaultHandler(val, filename, path):
    sec = ""
    for pattern in specialSections:
        if pattern.match(filename, path):
            sec = pattern.name
            break
    return [(sec, val, filename, path)]


def glitchDescriptionSpecialHandler(val, filename, path):
    extracted = glitchEmoteExtractor.match(val)
    is_glitch = glitchIsHere.match(path)
    if extracted is None or is_glitch is None:
        return False
    emote = extracted.groups()[0]
    text = extracted.groups()[1]
    t = defaultHandler(text, filename, normpath(
        join(path, "glitchEmotedText")))
    e = defaultHandler(emote, filename, normpath(join(path, "glitchEmote")))
    return t + e


textHandlers = [
    glitchDescriptionSpecialHandler,
    defaultHandler
]

specialSharedPaths = {
    "glitchEmote": "glitchEmotes",
}

# 增加了输出不能识别的文件的列表能力！utf-8bom byebye！

def parseFile(filename):
    chunk = list()
    if basename(filename)not in ignore_filelist_patch and basename(filename).endswith('.patch'):
        print(basename(filename))
        with open_n_decode(filename, "r", "utf_8_sig") as f:
            try:
                if basename(filename) in patchfile_spciallist1:
                    string = trans_patch(f)
                elif basename(filename) in patchfile_spciallist2:
                    string = trans_patch(f)
                else:
                    string = trans_patch(f)
            except:
                print("Cannot parse " + filename)
                problem_file = open(pro_list,'a')
                problem_file.writelines(filename.replace(root_dir,'')+'\n')
                problem_file.close()
                return []
            paths = to_a_list(string, 0)
            dialog = dirname(filename.replace('.patch', '')).endswith("dialog")
            for i, path in enumerate(paths):
                for k in files_of_interest.keys():
                    if filename.replace('.patch', '').endswith(k) or k == "*":
                        for roi in files_of_interest[k]:
                            if roi.match(path) or dialog:
                                val = to_a_list(string, 1)[i]
                                if not type(val) is str:
                                    print("File: " + filename)
                                    print("Type of " + path +
                                          " is not a string!")
                                    continue
                                if val == "":
                                    continue
                                for handler in textHandlers:
                                    res = handler(val, filename.replace(
                                        '.patch', ''), '/' + path)
                                    if res:
                                        chunk += res
                                        break
                                break
    return chunk



def construct_db(assets_dir):
    print("Scanning assets at " + assets_dir)
    db = dict()
    db[""] = dict()
    foi = list()
    patch = tuple('.patch')
    endings = tuple(files_of_interest.keys())
    for subdir, dirs, files in walk(assets_dir):
        for thefile in files:
            if thefile.endswith(patch):
                foi.append(normpath(join(subdir, thefile)))
    with Pool(8) as p:
        r = p.imap_unordered(parseFile, foi)
        for chunk in r:
            for sec, val, fname, path in chunk:
                if sec not in db:
                    db[sec] = dict()
                if val not in db[sec]:
                    db[sec][val] = dict()
                filename = normpath(
                    relpath(abspath(fname), abspath(assets_dir)))
                if filename not in db[sec][val]:
                    db[sec][val][filename.replace('.patch', '')] = list()
                if path not in db[sec][val][filename]:
                    insort_left(
                        db[sec][val][filename.replace('.patch', '')], path)
        return db


def file_by_assets(assets_fname, field, substitutions):
    if assets_fname in substitutions and field in substitutions[assets_fname]:
        return substitutions[assets_fname][field]
    else:
        return normpath(join(texts_prefix, assets_fname)) + ".json"


def process_label(combo):
    label, files, oldsubs, section = combo
    substitutions = dict()
    obj_file = normpath(getSharedPath(files.keys()))
    translation = dict()
    if section:
        translation["Comment"] = section
    translation["Texts"] = dict()
    translation["Texts"]["Eng"] = label
    translation["DeniedAlternatives"] = list()
    filename = ""
    for thefile, fields in files.items():
        for field in fields:
            fieldend = basename(field)
            if fieldend in specialSharedPaths:
                obj_file = normpath(specialSharedPaths[fieldend])
            if obj_file == '.':
                obj_file = "wide_spread_fields"
            filename = normpath(join(prefix, texts_prefix, obj_file + ".json"))
            if thefile != obj_file or fieldend in ["glitchEmotedText"]:
                if thefile not in substitutions:
                    substitutions[thefile] = dict()
                substitutions[thefile][field] = normpath(
                    relpath(filename, prefix))
            oldfile = normpath(
                join(prefix, file_by_assets(thefile, field, oldsubs)))
            if exists(oldfile):
                olddata = []
                try:
                    with open_n_decode(oldfile, 'r', 'utf-8') as f:
                        olddata = load(f)
                except:
                    pass
                for oldentry in olddata:
                    if oldentry["Texts"]["Eng"] == label:
                        if "DeniedAlternatives" in oldentry:
                            for a in oldentry["DeniedAlternatives"]:
                                if a not in translation["DeniedAlternatives"]:
                                    insort_left(
                                        translation["DeniedAlternatives"], a)
                        translation["Texts"].update(oldentry["Texts"])
                        break
    translation["Files"] = files
    return (filename, translation, substitutions)


def prepare_to_write(database):
    file_buffer = dict()
    substitutions = dict()
    oldsubs = dict()
    print("Trying to merge with old data...")
    try:
        with open_n_decode(sub_file, "r", 'utf-8') as f:
            oldsubs = load(f)
    except:
        print("No old data found, creating new database.")
    for section, thedatabase in database.items():
        with Pool(8) as p:
            result = p.imap_unordered(process_label,
                                      [(f, d, oldsubs, section) for f, d in thedatabase.items()], 40)
            for fn, js, sb in result:
                for fs, flds in sb.items():
                    if fs not in substitutions:
                        substitutions[fs] = flds
                    else:
                        substitutions[fs].update(flds)
                if fn not in file_buffer:
                    file_buffer[fn] = list()
                file_buffer[fn].append(js)
    file_buffer[sub_file] = substitutions
    return file_buffer


def catch_danglings(target_path, file_buffer):
    to_remove = list()
    for subdir, dirs, files in walk(target_path):
        for thefile in files:
            fullname = normpath(join(subdir, thefile))
            if thefile not in ignore_filelist:
                if fullname not in file_buffer:
                    to_remove.append(fullname)
    return to_remove


def write_file(filename, content):
    filedir = dirname(filename)
    if not filename.endswith("substitutions.json"):
        content = sorted(content, key=lambda x: x["Texts"]["Eng"])
    if len(filedir) > 0:
        makedirs(filedir, exist_ok=True)
    else:
        raise Exception("Filename without dir: " + filename)
    with open_n_decode(filename, "w", 'utf-8') as f:
        dump(content, f, ensure_ascii=False, indent=2, sort_keys=True)
        # print("Written " + filename)


# auto processing
def final_write(file_buffer):
    danglings = catch_danglings(join(prefix, "patches"), file_buffer)
    print("These files will be deleted:")
    for d in danglings:
        print('  ' + d)
        print('Writing...')
    with Pool(8) as p:
        delete_result = p.map_async(remove, danglings)
        write_result = p.starmap_async(write_file, list(file_buffer.items()))
        p.close()
        p.join()


'''
def final_write(file_buffer):
  danglings = catch_danglings(join(prefix, "texts"), file_buffer)
  print("These files will be deleted:")
  for d in danglings:
    print('  ' + d)
  print('continue? (y/n)')
  ans = get_answer(['y', 'n'])
  if ans == 'n':
    print('Cancelled!')
    return
  print('Writing...')
  with Pool() as p:
    delete_result = p.map_async(remove, danglings)
    write_result = p.starmap_async(write_file, list(file_buffer.items()))
    p.close()
    p.join()
'''
"""
if __name__ == "__main__":
    thedatabase = construct_db(root_dir)
    file_buffer = prepare_to_write(thedatabase)
    final_write(file_buffer)
    """


def extract_patch_labels(root_dir, prefix):
    open(pro_list,'w').truncate()
    root_dir = root_dir
    prefix = prefix
    thedatabase = construct_db(root_dir)
    file_buffer = prepare_to_write(thedatabase)
    final_write(file_buffer)

if __name__ == "__main__":
    root_dir = "F:\Starbound-RPG-Growth"
    prefix = "F:/Starbound-RPG-Growth-Chinese/translations"
    extract_patch_labels(root_dir, prefix)
