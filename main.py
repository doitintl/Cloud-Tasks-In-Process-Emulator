import datetime
import os

from flask import Flask, request

from tasks_access.tasks_access import CloudTasksAccessor

app = Flask(__name__)

QUEUE_NAME = 'my-appengine-queue'
LOCATION = 'us-central1'

cloud_tasks_client = None

task_count = 0


@app.route('/task_handler', methods=['POST'])
def task_handler():
    payload = request.get_data(as_text=True) or '<NO PAYLOAD>'
    queue_name = request.headers.get('X-AppEngine-QueueName')
    msg = handle_task(payload, queue_name)
    return msg


@app.route("/")
def create_task():
    scheduled_for = datetime.datetime.now() + datetime.timedelta(seconds=3)
    global task_count, cloud_tasks_client
    task_count += 1
    payload = f'Task #{task_count} created at {__format_datetime(datetime.datetime.now())}, ' \
              f'scheduled for {__format_datetime(scheduled_for)}'
    # In deployment, where the Emulator is not injected to cloud_tasks_client for development,
    # we will use the CloudTasksAccessor to access the real Cloud Tasks API.
    cloud_tasks_client = cloud_tasks_client or CloudTasksAccessor()
    cloud_tasks_client.create_task(QUEUE_NAME, payload, scheduled_for, __get_project_id(), LOCATION)
    return f'Sent "{payload}"'


def handle_task(payload: str, queue_path: str):
    """Callback for Cloud Tasks. To simulate processing, uppercase the payload, then print to standard output."""
    payload_upper = payload.upper()
    msg = f'Handling task from {queue_path.split("/")[-1]} with processed payload "{payload_upper}" ' \
          f'at {__format_datetime(datetime.datetime.now())}'
    print(msg)
    from_inside_handler = 'From inside handler, requeuing: '
    if from_inside_handler not in payload:  # avoid infinite regress
        global cloud_tasks_client
        requeued = from_inside_handler + payload
        cloud_tasks_client.create_task(QUEUE_NAME, requeued, None, __get_project_id(), LOCATION)
    return msg


def __format_datetime(dt):
    return dt.strftime('%H:%M:%S.%f')[:-3]


def __get_project_id():
    project_id = os.getenv('GAE_APPLICATION') or ''
    if project_id[1] == '~':
        project_id = project_id[2:]
    return project_id
