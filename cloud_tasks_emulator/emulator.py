import logging
import sys
import threading
import time
from datetime import datetime
from typing import Callable, List

log: logging.Logger


def init_logger():
    global log
    log = logging.getLogger(__name__)

    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)# Set to logging.INFO for logging to stdout
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


init_logger()


class Task:
    def __init__(self, payload, scheduled_for: float = None):
        self.payload = payload
        self.scheduled_for = scheduled_for or time.time()

    def __str__(self):
        return f"\"'{self.payload}', scheduled for {format_timestamp(self.scheduled_for)}\""


class Emulator:
    """
  The queues in the Emulator are not FIFO. Rather, they are priority queues: Popped in order of the time they are scheduled for.
  We sort by scheduled_for so that earliest delivery time is at the head of the queue, at index 0.
  Python sort is stable, so two tasks with the same delivery time will be processed FIFO.
    """

    def __init__(self, task_handler: Callable[[str], None]):
        self.__queue_threads: dict[str, threading.Thread] = {}
        self.__queues: dict[str, List[Task]] = {}
        self.__task_handler = task_handler
        self.__lock = threading.Lock()

    def __process_queue(self, queue_path):
        while True:
            with self.__lock:
                queue = self.__queues[queue_path]
                if queue:
                    peek = queue[0]
                    now: float = time.time()
                    if peek.scheduled_for <= now:
                        task: Task = queue.pop(0)  # Pop the beginning; push to the end
                        self.__task_handler(task.payload)
                        log.info(f"Processed task from queue {queue_path}: Task {task}")
                    else:
                        log.info(
                            f"Task was not ready at time {format_timestamp(now)}; "
                            f"scheduled for  {format_timestamp(peek.scheduled_for)}")
                time.sleep(0.01)

    def create_task(self, queue_name, payload, scheduled_for: datetime, project, location):
        """
        :param queue_name:  The name of the queue. If the queue does not yet exist
        in this emulator, it will be created.
        :param payload: A string that will be passed to the handler.
        :param scheduled_for: When this should be delivered
        :param project: If this is None or empty, "dummy-project" will be used.
        :param location: If this is None or empty, "dummy-location" will be used.
        :return: None
        """
        project=project or "dummy-project"
        location=location or "dummy-location"
        queue_path = f"projects/{project}/locations/{location}/queues/{queue_name}"
        with self.__lock:
            if queue_path not in self.__queues:
                self.__queues[queue_path] = []
                new_thread = threading.Thread(
                    target=self.__process_queue,
                    name=f"Thread-{queue_name}",
                    args=[queue_path],
                    daemon=True
                )
                self.__queue_threads[queue_path] = new_thread
                new_thread.start()
                log.info("Created queue " + queue_path)
            queue_name = self.__queues[queue_path]
            task = Task(payload, scheduled_for.timestamp())
            queue_name.append(task)

            log.info(f"Enqueued in queue {queue_path}; Task {task}")

            queue_name.sort(key=lambda t: t.scheduled_for)

    def total_enqueued_tasks(self):
        return sum(len(q) for q in self.__queues.values())


def format_timestamp(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S.%f")[:-3]
