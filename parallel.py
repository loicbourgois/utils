import asyncio
import functools
import time
from datetime import timedelta
from . import logging
from functools import wraps, partial


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


async def parallel_async(
    data,
    function,
    loop_check=0.1,
    tabs=0,
    verbose=True,
    concurrency=20,
):
    start_time = time.time()
    spaces = "".join(["  " for _ in range(tabs)])
    logging.info(f"{spaces}[start] {len(data)} {function.__name__}()")
    queue = set()
    done = set()

    def clean(i, _):
        done.add(i)
        queue.discard(i)
        if verbose:
            duration_so_far = time.time() - start_time
            percent_done = len(done) / len(data)
            full_duration = duration_so_far / percent_done
            eta = int(full_duration - duration_so_far)
            eta = str(timedelta(seconds=eta))
            logging.info(
                f"{spaces}[ end ] {function.__name__}() {len(done)}/{len(data)} - ETA {eta}"
            )

    task_wrappers = []
    for i, x in enumerate(data):
        task_wrappers.append(
            {
                "input": x,
            }
        )
        task_wrapper = task_wrappers[i]
        while True:
            await asyncio.sleep(loop_check)
            if len(queue) < concurrency:
                break
        if verbose:
            logging.info(f"{spaces}[start] {function.__name__}() {i+1}/{len(data)}")
        queue.add(i)
        task_wrapper["task"] = asyncio.create_task(function(task_wrapper["input"]))
        task_wrapper["task"].add_done_callback(functools.partial(clean, i))
    for i, task_wrapper in enumerate(task_wrappers):
        task_wrapper["output"] = await task_wrapper["task"]
        del task_wrapper["task"]
        data[i] = task_wrapper["output"]
    return data


def parallel(data, function, **kwargs):
    if kwargs.get("limit") is not None:
        return asyncio.run(parallel_async(data[:limit], function, **kwargs))
    return asyncio.run(parallel_async(data, function, **kwargs))
