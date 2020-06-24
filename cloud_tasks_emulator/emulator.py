#!/usr/bin/env python

import threading
import time
from typing import Optional, Callable


class Task:
    def __init__(self, payload, in_seconds=None):
        self._payload = payload
        self._delivery_time = time.time() + in_seconds if in_seconds else None


class TaskEmul:

    def __init__(self, task_handler: Callable[[str], None]):
        self._queue_threads: dict[str, threading.Thread] = {}
        self._queues: dict[str, list] = {}
        self.task_handler = task_handler

    def _process_queue(self, queue_name):
        pass

    def enqueue_task(self, payload: str, queue_name: str, in_seconds: Optional[int]):
        if queue_name not in self._queues:
            self._queues[queue_name] = []
            thread = threading.Thread(
                target=self._process_queue, args=[queue_name]
            )
            self._queue_threads[queue_name] = thread
            self._queue_threads[queue_name].start()
        self._queues[queue_name].append(Task(payload, in_seconds))
