import atexit
import datetime
import logging
import os
import threading
import time
from typing import Callable, List, Optional

import jsonpickle


def __init_logger():
    log = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    fmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(fmt)
    log.addHandler(handler)
    return log


log = __init_logger()


class Task:
    def __init__(self, payload, queue_path, scheduled_for: float = None):
        self.payload = payload
        self.scheduled_for = scheduled_for or time.time()
        self.queue_path = queue_path


class Emulator:
    """
  The queues in the Emulator are not FIFO. Rather, they are priority queues: Elements are popped in the
  order of the time they are scheduled for, and only after the scheduled time.
    """

    __queue_state_hibernation_file = os.path.abspath('task-queue-state-json')

    def __init__(self, task_handler: Callable[[str, str], None]):
        self.__queues: dict[str, List[Task]] = self.__load() or {}
        tot = self.total_enqueued_tasks()
        if tot:  # Walrus in Python 3.8!
            log.info("Loaded %d tasks", tot)
        self.__queue_threads: dict[str, threading.Thread] = {}
        for queue_path in self.__queues:  # Launch threads for loaded queues if any
            self.__launch_queue_thread(queue_path, queue_path.split('/')[:-1])
        self.__task_handler = task_handler
        self.__lock = threading.Lock()
        atexit.register(self._save)

    def __load(self):
        try:
            with open(self.__queue_state_hibernation_file, 'r') as f:
                json_s = f.read()
                loaded = jsonpickle.decode(json_s)
                os.remove(self.__queue_state_hibernation_file)
                return loaded
        except FileNotFoundError:
            log.info("No persisted queue state found")
            return None

    def _save(self):
        if self.total_enqueued_tasks():
            with open(self.__queue_state_hibernation_file, 'w') as f:
                json_s = jsonpickle.encode(self.__queues)
                f.write(json_s)
                log.info("Persisted queue state to %s", self.__queue_state_hibernation_file)

    def __process_queue(self, queue_path):
        while True:
            task: Optional[Task]
            task = None
            with self.__lock:
                queue = self.__queues[queue_path]
                if queue:
                    peek = queue[0]
                    now: float = time.time()
                    if peek.scheduled_for <= now:
                        task = queue.pop(0)  # Pop the beginning; push to the end
            if task:
                self.__task_handler(task.payload, task.queue_path)

            time.sleep(0.01)

    def create_task(self, queue_name, payload, scheduled_for: datetime.datetime, project, location):
        """
        :param queue_name: If the queue does not yet exist in this emulator, it will be created.
        :param payload: A string that will be passed to the handler.
        :param scheduled_for: When this should be delivered. If None or 0, will schedule
        for immediate delivery.
        :param project: If this is None or empty, "dummy-project" will be used.
        :param location: If this is None or empty, "dummy-location" will be used.
        """
        project = project or "dummy-project"
        location = location or "dummy-location"
        scheduled_for = scheduled_for or datetime.datetime.now()
        queue_path = f"projects/{project}/locations/{location}/queues/{queue_name}"
        # todo don't use path
        with self.__lock:
            if queue_path not in self.__queues:
                self.__queues[queue_path] = []
                self.__launch_queue_thread(queue_path, queue_name)
            queue = self.__queues[queue_path]
            task = Task(payload, queue_path, scheduled_for.timestamp())
            queue.append(task)
            queue.sort(key=lambda t: t.scheduled_for)

    def __launch_queue_thread(self, queue_path, queue_name):
        new_thread = threading.Thread(target=self.__process_queue,
                                      name=f"Thread-{queue_name}", args=[queue_path], daemon=True)
        self.__queue_threads[queue_path] = new_thread
        new_thread.start()

    def total_enqueued_tasks(self):
        return sum(len(q) for q in self.__queues.values())
