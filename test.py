import datetime
from threading import current_thread
from time import sleep

from cloud_tasks_emulator.emulator import Emulator


def handle_tasks(payload: str):
    time_of_day = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"Received the payload \"{payload}\" at {time_of_day} in thread {current_thread().name}")


def main():
    queue_name = "queue1"
    base_delay_seconds = 4
    emul = Emulator(handle_tasks)
    for i in range(4):
        now = datetime.datetime.now()
        time_of_day = now.strftime("%H:%M:%S")
        offset = 4 if i % 2 else 0  # odd numbered messages delayed more, to test the delayed-delivery feature
        delay=base_delay_seconds+offset
        expected_delivery=now + datetime.timedelta(seconds=delay)
        expected_delivery_s= expected_delivery.strftime("%H:%M:%S")
        emul.enqueue_task(f"Payload #{i} was enqueued at {time_of_day} and should be delivered at {expected_delivery_s}", queue_name, base_delay_seconds)
        sleep(1)


if __name__ == '__main__':
    main()
