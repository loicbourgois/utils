# PYTHONPATH=$HOME/github.com/loicbourgois python3 -m utils.git
import os
from pandas import DataFrame
from .runcmd import runcmd_str
from .parallel import parallel
from functools import wraps, partial
import asyncio
import time
from random import random
import numpy as np


def list_repos(path):
    csvs = {}
    for path_1, _subdirs, files in os.walk(path):
        for name in files:
            x = os.path.join(path, name)
            if x.endswith(".csv"):
                csvs[x] = x
    return csvs


def flatten(list_of_list):
    list_ = []
    for x in list_of_list:
        list_.extend(x)
    return list_


def ls_with_full_path(paths):
    return [
        [
            f"{cwd}/{x}" 
            for x in runcmd_str(
                "ls", 
                cwd=cwd,
                quiet=True,
            )
        ] for cwd in paths
    ]


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


@async_wrap
def print_async(x):
    time.sleep(random())
    return print(x)


@async_wrap
def git_status_async(cwd):
    r = {
        'repo': cwd.split('/')[-1],
        'organization': cwd.split('/')[-2],
        'platform': cwd.split('/')[-3],
        'path': cwd.replace(os.environ['HOME'], "~"),
    }
    try:
        lines = runcmd_str(
            "git status -sb", 
            cwd=cwd,
            quiet=True,
        )
        r['c'] = len(lines)
        r['status'] = lines[0]
        if "[ahead" in lines[0]:
            r['ahead'] = "x"
    except:
        pass
    return r


if __name__ == "__main__":
    path = f"{os.environ['HOME']}/github.com/"
    platform_paths = [
        f"{os.environ['HOME']}/github.com",
        f"{os.environ['HOME']}/gitlab.com"
    ]
    organization_paths = flatten(ls_with_full_path(platform_paths))
    repository_paths = flatten(ls_with_full_path(organization_paths))
    data = parallel(
        repository_paths,
        git_status_async,
        concurrency=1000,
        verbose = False,
    )
    df = DataFrame(data, columns=['status', 'repo', 'organization', 'platform', 'path', 'c', 'ahead'])
    df = df[ df['c'] > 0 ]
    df = df.replace(np.nan, '')
    df = df.sort_values(
        by=['c', 'ahead'],
        ascending=[True, True],
    )
    print(df)
