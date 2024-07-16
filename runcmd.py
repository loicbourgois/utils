import uuid
import subprocess
import os
import time
from . import logging


def short_path(x):
    return x


def grey(x):
    return x


runcmd_list_stdouts = {}


def runcmd_str(cmd: str, **kwargs):
    return runcmd_list(cmd.split(" "), **kwargs)


def runcmd_list(
    command: list,
    quiet=False,
    parallel=False,
    cwd=None,
    env=None,
    ignore_return_code=False,
):
    if not quiet:
        for line in " ".join(command).split("\n"):
            dir_str = ""
            if cwd:
                dir_str = grey(f" # in {cwd}")
            line = short_path("$ " + line + dir_str)
            if parallel:
                line = f"[{os.getpid()}]" + line
            logging.info(line)

    def stream_process(process, command_id):
        go = process.poll() is None
        for line in process.stdout:
            l = os.linesep.join([s for s in line.decode("UTF8").splitlines() if s])
            if not quiet:
                if parallel:
                    logging.info((f"  [{os.getpid()}] {l}"))
                else:
                    logging.info(("  " + l))
            runcmd_list_stdouts[command_id].append(l)
        return go

    command_id = str(uuid.uuid4())
    runcmd_list_stdouts[command_id] = []
    if env:
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env=env,
        )
    else:
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )
    while stream_process(process, command_id):
        time.sleep(0.1)
    if not ignore_return_code:
        assert (
            process.returncode == 0
        ), f"invalid returncode: expected 0, got {process.returncode} - command: {command}"
    return runcmd_list_stdouts[command_id]
