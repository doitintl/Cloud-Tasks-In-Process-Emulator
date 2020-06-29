import datetime
import os

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from flask import Flask, request

app = Flask(__name__)

@app.route("/task_handler", methods=["POST"])
def task_handler():
    payload = request.get_data(as_text=True) or "<NO PAYLOAD>"
    msg= f"Task Received: {payload}"
    print(msg)
    return msg

@app.route("/")
def send_task():
    app_id = os.getenv('GAE_APPLICATION')
    if not app_id: raise Exception("GAE_APPLICATION env variable must be specified")
    in_seconds=3
    scheduled_for = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)
    payload = f"This task was sent at {datetime.datetime.now().isoformat()} and should be delivered at {scheduled_for.isoformat()}"
    #TODO PROJECT
    from tasks_access.tasks_access import create_task
    create_task(app_id, "my-appengine-queue", "us-central1",  payload)
    return f'Sent "{payload}"'




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
