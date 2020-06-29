import logging
import sys
import threading
import time
from datetime import datetime
from typing import Callable

log: logging.Logger


def init_logger():
    global log
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


init_logger()


class Task:
    def __init__(self, payload, scheduled_for: float = None):
        self.payload = payload
        if scheduled_for is None:
            self.scheduled_for = time.time()
        else:
            self.scheduled_for = scheduled_for

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
        self.__queues: dict[str, list[Task]] = {}
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
                            f"scheduld for  {format_timestamp(peek.scheduled_for)}")
                time.sleep(0.01)

    def create_task(self, tasks_on_queue, payload, scheduled_for: datetime, project, location):
        queue_path = f"projects/{project}/locations/{location}/queues/{tasks_on_queue}"
        with self.__lock:
            if queue_path not in self.__queues:
                self.__queues[queue_path] = []
                new_thread = threading.Thread(
                    target=self.__process_queue,
                    name=f"Thread-{tasks_on_queue}",
                    args=[queue_path],
                    daemon=True
                )
                self.__queue_threads[queue_path] = new_thread
                new_thread.start()
                log.info("Created queue " + queue_path)
            tasks_on_queue = self.__queues[queue_path]
            task = Task(payload, scheduled_for.timestamp())
            tasks_on_queue.append(task)

            log.info(f"Enqueued in queue {queue_path}; Task {task}")

            tasks_on_queue.sort(key=lambda t: t.scheduled_for)

    def total_enqueued_tasks(self):
        return sum(len(q) for q in self.__queues.values())


def format_timestamp(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S.%f")[:-3]
