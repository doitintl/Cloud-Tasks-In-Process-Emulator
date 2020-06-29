from datetime import datetime

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2


class CloudTasksAccessor:
    def create_task(self, queue_name, payload, scheduled_for: datetime, project, location):
        assert project, "Must provide project ID"
        assert location, "Must provide location"
        scheduled_for= scheduled_for or  datetime.now()
        payload =payload or ""

        client = tasks_v2.CloudTasksClient()
        queue_path = client.queue_path(project, location, queue_name)

        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(scheduled_for)
        task = {
            "app_engine_http_request": {
                "http_method": "POST",
                "relative_uri": "/task_handler",
                "body": payload.encode()
            },
            "schedule_time": timestamp
        }

        response = client.create_task(queue_path, task)
        print(f'Created "task {response.name}" at {queue_path}')
        return response
