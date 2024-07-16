import os
from pathlib import Path

def write(path=None, content=None):
    assert path is not None
    assert content is not None
    with open(path, "w") as file:
        file.write(content)


def write_force(path, content):
    folder = path.replace(path.split("/")[-1], "")
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(path, "w") as f:
        f.write(content)


def read(path):
    with open(path, "r") as file:
        return file.read()


def file_exists(path):
    return os.path.exists(path)


def list_all_files(path, filter_):
    return list(Path(path).rglob(filter_))
