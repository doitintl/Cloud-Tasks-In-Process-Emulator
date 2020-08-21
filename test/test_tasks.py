import json
import logging
import time
import unittest
from collections import defaultdict
from datetime import datetime
from threading import current_thread
from time import sleep
from typing import List

from cloud_tasks_emulator.emulator import Emulator

log = logging.getLogger(__name__)


class TestEmulator(unittest.TestCase):
    def __init__(self, name='test'):
        super().__init__(name)
        self.TASKS_PER_QUEUE = 4
        self.DELAY_EVEN_NUMBERED_TASKS = 3
        self.NUM_QUEUES = 4

        self.received: dict[str, List[str]] = defaultdict(list)

    def test_enqueue_dequeue(self):
        emulator = Emulator(self.handle_tasks, hibernation=False)
        max_scheduled_for = self.__enqueue_test_tasks(emulator)
        self.__wait_for_handling(emulator, max_scheduled_for)

    def handle_tasks(self, payload: str, q_name_from_handler: str):

        def format_timestamp(timestamp: float) -> str:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%H:%M:%S.%f')[:-3]

        now = time.time()
        thread_name = current_thread().name
        payload_contents = json.loads(payload)
        q_name_from_payload = payload_contents['q_name']
        q_name_from_thread = thread_name.split('-')[1]
        self.received[q_name_from_payload].append(payload_contents)
        scheduled_for = payload_contents['scheduled_for']
        insertion_index = payload_contents['insertion_index']
        diff_in_seconds = scheduled_for - now

        log.info(f'Handling task on queue {q_name_from_handler} '
                 f'with insertion #{insertion_index} from {q_name_from_payload} '
                 f'scheduled for {format_timestamp(scheduled_for)} at '
                 f'{format_timestamp(now)} ({round(-1000 * diff_in_seconds)} ms late); using {thread_name}')

        self.__assertionsOnReceivedTasks(diff_in_seconds, format_timestamp, now, q_name_from_thread,
                                         q_name_from_handler, scheduled_for,
                                         payload_contents, q_name_from_payload)

    def __assertionsOnReceivedTasks(self, diff_in_seconds, format_timestamp, now, q_name_from_thread,
                                    q_name_from_handler, scheduled_for, task, q_name_from_payload):
        self.assertLessEqual(diff_in_seconds, 0, f'Expect to process tasks on or after scheduled time, not before')
        max_late = 1.5
        self.assertGreater(diff_in_seconds, -max_late,
                           msg=
                           f'task {task}\nfor {format_timestamp(scheduled_for)} is more than '
                           f'{max_late} seconds late compared to  '
                           f'{format_timestamp(now)} by {diff_in_seconds} seconds')
        self.assertEqual(q_name_from_payload, q_name_from_thread,
                         f'Thread name {q_name_from_thread} != '
                         f'queue name passed in task payload {q_name_from_payload}')
        self.assertEqual(q_name_from_payload, q_name_from_handler,
                         f'Queue name {q_name_from_handler} from handler != '
                         f'queue name passed in task payload {q_name_from_payload}')

    def __wait_for_handling(self, emulator, max_scheduled_for):
        while emulator.total_enqueued_tasks() and time.time() < max_scheduled_for + 1:
            sleep(0.01)
        self.__assertionsOnCompletion()

    def __assertionsOnCompletion(self):
        for q_name, tasks_received in self.received.items():
            self.assertEqual(len(tasks_received), self.TASKS_PER_QUEUE,
                             f'Received {len(tasks_received)} in queue {q_name}, but expect {self.TASKS_PER_QUEUE}')
            sorted_tasks = sorted(tasks_received, key=lambda json_task: json_task['scheduled_for'])
            self.assertEqual(sorted_tasks, tasks_received,
                             f'Tasks received from queue {q_name} wrong; maybe in wrong order: {tasks_received} ')

    def __enqueue_test_tasks(self, emulator):
        max_scheduled_for = time.time()
        for queue_num in range(self.NUM_QUEUES):
            q_name = f'q{queue_num}'
            for insertionIndex in range(self.TASKS_PER_QUEUE):
                delay = 0 if insertionIndex % 2 else self.DELAY_EVEN_NUMBERED_TASKS
                now: float = time.time()
                scheduled_for = now + delay
                max_scheduled_for = max(max_scheduled_for, scheduled_for)
                payload = {'insertion_index': insertionIndex,
                           'q_name': q_name,
                           'scheduled_for': scheduled_for}
                project = 'sample_project'
                location = 'mars-west2'
                emulator.create_task(q_name, json.dumps(payload),
                                     datetime.fromtimestamp(scheduled_for), project, location)
                sleep(0.2)
        return max_scheduled_for
