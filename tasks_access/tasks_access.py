#!/usr/bin/env python
import json
import logging
import sys
import threading
import time
from datetime import datetime
from typing import Callable

class CloudTasksClient:
  def create_task(self, project, queue, location, payload, scheduled_for:datetime=None):
    if not scheduled_for:scheduled_for=datetime.datetime.now()

    assert payload
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(project, location, queue)

    task = {
        "app_engine_http_request": {
            "http_method": "POST",
            "relative_uri": "/task_handler"
            }
    }
    converted_payload = payload.encode()
    task["app_engine_http_request"]["body"] = converted_payload

    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(scheduled_for)
    task["schedule_time"] = timestamp

    response = client.create_task(parent, task)
    print(f'Created "task {response.name}"')
    return response
