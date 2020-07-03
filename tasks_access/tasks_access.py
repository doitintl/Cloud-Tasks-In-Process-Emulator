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
Traceback (most recent call last): File "/env/lib/python3.7/site-packages/flask/app.py", line 2447, in wsgi_app response = self.full_dispatch_request() File "/env/lib/python3.7/site-packages/flask/app.py", line 1952, in full_dispatch_request rv = self.handle_user_exception(e) File "/env/lib/python3.7/site-packages/flask/app.py", line 1821, in handle_user_exception reraise(exc_type, exc_value, tb) File "/env/lib/python3.7/site-packages/flask/_compat.py", line 39, in reraise raise value File "/env/lib/python3.7/site-packages/flask/app.py", line 1950, in full_dispatch_request rv = self.dispatch_request() File "/env/lib/python3.7/site-packages/flask/app.py", line 1936, in dispatch_request return self.view_functions[rule.endpoint](**req.view_args) File "/srv/main.py", line 35, in send_task cloud_tasks_client.create_task(QUEUE_NAME, payload, scheduled_for, project_id, LOCATION) File "/srv/tasks_access/tasks_access.py", line 28, in create_task response = client.create_task(queue_path, task) File "/env/lib/python3.7/site-packages/google/cloud/tasks_v2/gapic/cloud_tasks_client.py", line 1508, in create_task request, retry=retry, timeout=timeout, metadata=metadata File "/env/lib/python3.7/site-packages/google/api_core/gapic_v1/method.py", line 143, in __call__ return wrapped_func(*args, **kwargs) File "/env/lib/python3.7/site-packages/google/api_core/retry.py", line 286, in retry_wrapped_func on_error=on_error, File "/env/lib/python3.7/site-packages/google/api_core/retry.py", line 184, in retry_target return target() File "/env/lib/python3.7/site-packages/google/api_core/timeout.py", line 214, in func_with_timeout return func(*args, **kwargs) File "/env/lib/python3.7/site-packages/google/api_core/grpc_helpers.py", line 59, in error_remapped_callable six.raise_from(exceptions.from_grpc_error(exc), exc) File "<string>", line 3, in raise_from google.api_core.exceptions.PermissionDenied: 403 Permission denied on resource project s~joshua-playground.