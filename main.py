import datetime

from cloud_tasks_emulator.emulator import TaskEmul


def handle_tasks(payload: str):
    print(f"Received the payload {payload} at {datetime.datetime.now()}")


def main():
    queue_name = "queue1"
    in_seconds = None
    emul = TaskEmul(handle_tasks)
    emul.enqueue_task("my-payload", queue_name, in_seconds)


if __name__ == '__main__':
    main()
