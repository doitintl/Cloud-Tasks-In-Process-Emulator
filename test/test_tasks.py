import json
import time
import unittest
from collections import defaultdict
from datetime import datetime
from threading import current_thread
from time import sleep
from typing import List

from cloud_tasks_emulator.emulator import Emulator


class TestEmulator(unittest.TestCase):
    def __init__(self, name="test"):
        super().__init__(name)
        self.TASKS_PER_QUEUE = 4
        self.DELAY_EVEN_NUMBERED_TASKS = 3
        self.NUM_QUEUES = 4

        self.received: dict[str, List[str]] = defaultdict(list)

    def handle_tasks(self, payload: str, queue_path: str):

        def format_timestamp(timestamp: float) -> str:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%H:%M:%S.%f")[:-3]

        now = time.time()
        thread_name = current_thread().name
        task = json.loads(payload)
        task_queue_name = task["queue_name"]
        queue_name_from_thread = thread_name.split("-")[1]
        self.received[task_queue_name].append(task)
        scheduled_for = task["scheduled_for"]
        insertion_index = task["insertion_index"]
        diff_in_seconds = scheduled_for - now

        print(f"""Handling task on queue {self.__queue_name_from_path(queue_path)} \
with insertion #{insertion_index} from {task_queue_name} \
scheduled for {format_timestamp(scheduled_for)} at \
{format_timestamp(now)} ({round(-1000 * diff_in_seconds)} ms late); using {thread_name}""")

        self.__assertionsOnReceivedTasks(diff_in_seconds, format_timestamp, now, queue_name_from_thread, queue_path,
                                         scheduled_for, task, task_queue_name)

    def __assertionsOnReceivedTasks(self, diff_in_seconds, format_timestamp, now, queue_name_from_thread, queue_path,
                                    scheduled_for, task, task_queue_name):
        self.assertLessEqual(diff_in_seconds, 0, f"Expect to process tasks on or after scheduled time, not before")
        max_late = 1.5
        self.assertGreater(diff_in_seconds, -max_late,
                           msg=
                           f"task {task}\nfor {format_timestamp(scheduled_for)} is  more than {max_late} seconds late compared to  "
                           f"{format_timestamp(now)} by {diff_in_seconds} seconds")
        self.assertEqual(task_queue_name, queue_name_from_thread,
                         f"Wrong thread name {queue_name_from_thread} as compared to queue name passed in task payload {task_queue_name}")
        queue_name = self.__queue_name_from_path(queue_path)
        self.assertEqual(task_queue_name, queue_name_from_thread,
                         f"Wrong queue name from path {queue_name} as compared to queue name passed in task payload {task_queue_name}")

    def __queue_name_from_path(self, queue_path):
        return queue_path.split("/")[-1]

    def test_enqueue_dequeue(self):
        emulator = Emulator(self.handle_tasks)
        max_scheduled_for = self.__enqueue_test_tasks(emulator)
        self.__wait_for_handling(emulator, max_scheduled_for)

    def __wait_for_handling(self, emulator, max_scheduled_for):
        while emulator.total_enqueued_tasks() and time.time() < max_scheduled_for + 1:
            sleep(0.01)
        self.__assertionsOnCompletion()

    def __assertionsOnCompletion(self):
        for queue_name, tasks_received in self.received.items():
            self.assertEqual(len(tasks_received), self.TASKS_PER_QUEUE,
                             f"Received {len(tasks_received)} in queue {queue_name}, but expect {self.TASKS_PER_QUEUE}")
            sorted_tasks = sorted(tasks_received, key=lambda json_task: json_task['scheduled_for'])
            self.assertEqual(sorted_tasks, tasks_received,
                             f"Tasks received from queue {queue_name} wrong; maybe in wrong order: {tasks_received} ")

    def __enqueue_test_tasks(self, emulator):
        max_scheduled_for = time.time()
        for queue_num in range(self.NUM_QUEUES):
            queue_name = f"q{queue_num}"
            for insertionIndex in range(self.TASKS_PER_QUEUE):
                delay = 0 if insertionIndex % 2 else self.DELAY_EVEN_NUMBERED_TASKS
                now: float = time.time()
                scheduled_for = now + delay
                max_scheduled_for = max(max_scheduled_for, scheduled_for)
                payload = {"insertion_index": insertionIndex,
                           "queue_name": queue_name,
                           "scheduled_for": scheduled_for}
                project = "sample_project"
                location = "mars-west2"
                emulator.create_task(queue_name, json.dumps(payload),
                                     datetime.fromtimestamp(scheduled_for), project, location)
                sleep(0.2)
        return max_scheduled_for
