import os
import re
import glob
import yaml


def load_cfg(path: str):
    return yaml.safe_load(open(path, "r"))


def load_script(path: str):
    return open(path, "r").read()


def save_script(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


def is_valid_dir(path: str, extensions: list) -> bool:
    for _, _, files in os.walk(path):
        if any(filename.endswith(ext) for filename in files for ext in extensions):
            return True
    return False


def find_file_variants(filename: str, as_dict: bool = False) -> list:
    base_name, ext = os.path.splitext(filename)
    base_name = re.sub(r"\[\d+\]", "", base_name)
    files = glob.glob(f"{base_name}*{ext}")
    pattern = re.compile(rf"{base_name}\[\d+\]{ext}")
    variants = sorted(glob.glob(f"{base_name}{ext}") + [f for f in files if pattern.search(f)])
    if as_dict:
        variants = {extract_variant_id(filename): filename for filename in variants}
    return variants


def extract_variant_id(filename: str) -> str:
    split_filename = re.search(r"\[(\d+)\](?!.*\[\d+\])", filename)
    if split_filename is None:
        return 0
    return int(split_filename.group(1))


def is_valid_file(path: str, extensions: list, hide_file_variants: bool = True) -> bool:

    # Check extension
    if not any(path.endswith(ext) for ext in extensions) is True:
        return False

    if hide_file_variants is True:
        # Check if path is either the original file or first of the (sorted) copies
        variants = sorted(find_file_variants(path))
        return path == variants[0]
    else:
        return True
