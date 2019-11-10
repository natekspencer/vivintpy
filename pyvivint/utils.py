import asyncio
from typing import Callable


def first_or_none(lst, predicate):
    filter_iter = filter(predicate, lst)
    return next(filter_iter, None)


def add_async_job(target: Callable, *args):
    loop = asyncio.get_event_loop()

    if asyncio.iscoroutine(target):
        task = loop.create_task(target)
    elif asyncio.iscoroutinefunction(target):
        task = loop.create_task(target(*args))
    else:
        task = loop.run_in_executor(None, target, *args)

    return task
