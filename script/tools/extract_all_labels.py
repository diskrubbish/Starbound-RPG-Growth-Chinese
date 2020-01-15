from extract_labels import extract_labels
from extract_patch_labels import extract_patch_labels
root_dir = "F:\Starbound-RPG-Growth"
prefix = "F:/Starbound-RPG-Growth-Chinese/translations"
if __name__ == "__main__":
    print("1：Extract the normal labels")
    extract_labels(root_dir,prefix)
    print("2：Extract the patch's labels")
    extract_patch_labels(root_dir,prefix)

    