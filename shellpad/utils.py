import yaml


def load_cfg(path: str) -> dict:
    return yaml.safe_load(open(path, "r"))


def load_script(path: str) -> str:
    return open(path, "r").read()


def save_script(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)
