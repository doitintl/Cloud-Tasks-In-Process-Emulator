import json
import time
import unittest
from collections import Counter, defaultdict
from threading import current_thread
from time import sleep

from cloud_tasks_emulator.emulator import Emulator, format_timestamp


class TestEmulator(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.TASKS_PER_QUEUE = 4
        self.DELAY_EVEN_NUMBERED_TASKS = 3
        self.NUM_QUEUES = 4

        self.received:dict[str, list[str]] = defaultdict(list)

    def handle_tasks(self, payload: str):
        now = time.time()
        thread_name = current_thread().name
        task = json.loads(payload)
        task_queue_name = task["queue_name"]
        queue_name_from_thread = thread_name.split("-")[1]
        self.received[task_queue_name].append(task)
        scheduled_for = task["scheduled_for"]
        insertion_index = task["insertion_index"]
        diff_in_seconds = scheduled_for - now
        self.assertLess(diff_in_seconds, 0, f"Expect to process tasks after schedule time, not before")
        self.assertGreater(diff_in_seconds, -0.7,
                           msg=
                           f"task {task}\nfor {format_timestamp(scheduled_for)} differs "
                           f"from current {format_timestamp(now)}, difference was {diff_in_seconds}")

        print(f"""Handling task with insertion #{insertion_index} from \
{task_queue_name} scheduled for {format_timestamp(scheduled_for)} at \
{format_timestamp(now)} ({round(-1000*diff_in_seconds)} ms late); using {thread_name}""")

        self.assertEqual(task_queue_name, queue_name_from_thread)


    def test_enqueue_dequeue(self):
        emulator = Emulator(self.handle_tasks)
        max_scheduled_for = self.__enqueue_test_tasks(emulator)
        self.__wait_for_handling(emulator, max_scheduled_for)

    def __wait_for_handling(self, emulator, max_scheduled_for):
        while emulator.total_enqueued_tasks() and time.time() < max_scheduled_for + 1:
            sleep(0.01)
        for queue_name, tasks_received in self.received.items():
            self.assertEqual(len(tasks_received), self.TASKS_PER_QUEUE,
                             f"Received {len(tasks_received)} in queue {queue_name}")
            sorted_tasks=sorted(tasks_received, key=lambda jsonTask: jsonTask['scheduled_for'])
            self.assertEqual(sorted_tasks, tasks_received)

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

                emulator.enqueue_task(json.dumps(payload), queue_name, scheduled_for)
                sleep(0.2)
        return max_scheduled_for


TestEmulator().test_enqueue_dequeue()
