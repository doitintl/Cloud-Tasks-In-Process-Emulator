#!/usr/bin/env python
import logging
import threading
import time
from datetime import datetime
from typing import Optional, Callable

log = logging.getLogger(__name__)
# TODO set up log

class Task:
    def __init__(self, payload, delay_seconds=0):
        self.payload = payload
        self.delivery_time = time.time() + delay_seconds if delay_seconds else None


class Emulator:
    def __init__(self, task_handler: Callable[[str], None]):
        self.__queue_threads: dict[str, threading.Thread] = {}
        self.__queues: dict[str, list[Task]] = {}
        self.__task_handler = task_handler
        self.__lock = threading.Lock()

    def __process_queue(self, queue_name):
        while True:
            with self.__lock:
                q = self.__queues[queue_name]
                if q:
                    peek=q[0]
                    if peek.delivery_time>=time.time():
                      task: Task = q.pop(0)  # Pop the beginning; push to the end
                      self.__task_handler(task.payload)
                      log.info("Processed task from queue", queue_name)
                time.sleep(0.1)

    def enqueue_task(self, payload: str, queue_name: str, in_seconds: Optional[int]):
        with self.__lock:
            if queue_name not in self.__queues:
                self.__queues[queue_name] = []
                new_thread = threading.Thread(
                    target=self.__process_queue,
                    name=f"Thread-{queue_name}",
                    args=[queue_name],
                    daemon=True
                )
                self.__queue_threads[queue_name] = new_thread
                new_thread.start()
                log.info("Created queue", queue_name)
            q = self.__queues[queue_name]

            q.append(Task(payload, in_seconds))

            log.info("Enqueued in queue", queue_name)
            # We sort by delivery_time so that earliest delivery
            # time is at the head of the queue, ready to be popped.
            # Python sort is stable, so two tasks with the same delivery
            # time will be processed FIFO.
            # Note that if tasks are always added for immediate
            # delivery (with in_seconds=0), then the earlier one will have
            # a lower delivery time and so will be at the head of the queue.
            q.sort(key=lambda task: task.delivery_time)
