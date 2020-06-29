import datetime
import os

from flask import Flask, request

from sample_app.tasks_access import CloudTasksAccessor

app = Flask(__name__)

queue_name = "my-appengine-queue"
location = "us-central1"
global cloud_tasks_client


@app.route("/task_handler", methods=["POST"])
def task_handler():
    payload = request.get_data(as_text=True) or "<NO PAYLOAD>"
    msg = handle_task(payload)
    return msg


@app.route("/")
def send_task():
    app_id = os.getenv('GAE_APPLICATION')
    if not app_id: raise Exception("GAE_APPLICATION env variable must be specified")
    in_seconds = 3
    scheduled_for = datetime.datetime.now() + datetime.timedelta(seconds=in_seconds)
    payload = f"This task was sent at {format_datetime(datetime.datetime.now())}, scheduled for {format_datetime(scheduled_for)}"
    global cloud_tasks_client
    if cloud_tasks_client is None:
        cloud_tasks_client = CloudTasksAccessor()
    cloud_tasks_client.create_task(queue_name, payload, scheduled_for, app_id, "us-central1")
    return f'Sent "{payload}"'


def handle_task(payload: str):
    payload_upper = payload.upper()
    msg = f'Handling the payload: "{payload_upper}" at {format_datetime(datetime.datetime.now())}'
    print(msg)
    return msg


def format_datetime(dt):
    return dt.strftime("%H:%M:%S.%f")[:-3]
