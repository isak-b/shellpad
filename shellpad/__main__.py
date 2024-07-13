import os
import sys

from utils import load_cfg
from app import ShellPad

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CFG_PATH = os.path.join(ROOT_PATH, "config.yaml")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = load_cfg(sys.argv[1])
    else:
        path = os.getcwd()

    cfg = load_cfg(DEFAULT_CFG_PATH)
    app = ShellPad(path=path, cfg=cfg)
    app.run()
