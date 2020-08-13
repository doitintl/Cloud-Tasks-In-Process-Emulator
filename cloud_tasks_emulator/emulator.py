import threading
import time
from datetime import datetime
from typing import Callable, List, Optional


class Task:
    def __init__(self, payload, queue_path, scheduled_for: float = None):
        self.payload = payload
        self.scheduled_for = scheduled_for or time.time()
        self.queue_path = queue_path


count = 0


class Emulator:
    """
  The queues in the Emulator are not FIFO. Rather, they are priority queues: Elements are popped in the
  order of the time they are scheduled for, and only after the scheduled time.
    """

    def __init__(self, task_handler: Callable[[str, str], None]):
        self.__queue_threads: dict[str, threading.Thread] = {}
        self.__queues: dict[str, List[Task]] = {}
        self.__task_handler = task_handler
        self.__lock = threading.Lock()

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

    def create_task(self, queue_name, payload, scheduled_for: datetime, project, location):
        """
        :param queue_name: If the queue does not yet exist in this emulator, it will be created.
        :param payload: A string that will be passed to the handler.
        :param scheduled_for: When this should be delivered
        :param project: If this is None or empty, "dummy-project" will be used.
        :param location: If this is None or empty, "dummy-location" will be used.
        """
        project = project or "dummy-project"
        location = location or "dummy-location"
        queue_path = f"projects/{project}/locations/{location}/queues/{queue_name}"
        with self.__lock:
            if queue_path not in self.__queues:
                self.__queues[queue_path] = []
                new_thread = threading.Thread(target=self.__process_queue,
                                              name=f"Thread-{queue_name}", args=[queue_path], daemon=True)
                self.__queue_threads[queue_path] = new_thread
                new_thread.start()
            queue = self.__queues[queue_path]
            task = Task(payload, queue_path, scheduled_for.timestamp())
            queue.append(task)
            queue.sort(key=lambda t: t.scheduled_for)

    def total_enqueued_tasks(self):
        return sum(len(q) for q in self.__queues.values())
