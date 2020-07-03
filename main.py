import datetime
import os

from flask import Flask, request

from tasks_access.tasks_access import CloudTasksAccessor

app = Flask(__name__)

QUEUE_NAME = "my-appengine-queue"
LOCATION = "us-central1"

cloud_tasks_client = None


@app.route("/task_handler", methods=["POST"])
def task_handler():
    payload = request.get_data(as_text=True) or "<NO PAYLOAD>"
    queue_name = request.headers.get("X-AppEngine-QueueName")
    msg = handle_task(payload, queue_name)
    return msg


@app.route("/")
def create_task():
    project_id = os.getenv("GAE_APPLICATION") or ""
    if project_id[0:2] == 's~':
        project_id=project_id[2:]

    in_seconds = 3
    scheduled_for = datetime.datetime.now() + datetime.timedelta(seconds=in_seconds)
    payload = f"This task was created at {format_datetime(datetime.datetime.now())}, " \
              f"scheduled for {format_datetime(scheduled_for)}"
    global cloud_tasks_client
    # In deployment, where the Emulator is not injected to cloud_tasks_client for development, we will use
    # the CloudTasksAccessor to access the real Cloud Tasks API.
    cloud_tasks_client = cloud_tasks_client or CloudTasksAccessor()
    cloud_tasks_client.create_task(QUEUE_NAME, payload, scheduled_for, project_id, LOCATION)
    return f'Sent "{payload}"'


def handle_task(payload: str, queue_path: str):
    """Callback for Cloud Tasks. To simulate processing, uppercase the paylad, then print to standard output."""
    payload_upper = payload.upper()
    msg = f'Handling task from queue {queue_path} with payload "{payload_upper}" at {format_datetime(datetime.datetime.now())}'
    print(msg)
    return msg


def format_datetime(dt):
    return dt.strftime("%H:%M:%S.%f")[:-3]
