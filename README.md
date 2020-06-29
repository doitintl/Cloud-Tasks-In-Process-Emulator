# In-Process Simple Emulator for Google Cloud Tasks
Google [doesn't](https://cloud.google.com/tasks/docs/migrating#features_in_task_queues_not_yet_available_via)
[offer](https://issuetracker.google.com/issues/133627244)
an emulator for the Cloud Tasks API,  as it does for Datastore or PubSub. This project answers that need.

# Usage

To use this emulator, copy `emulator.py` into your codebase. Create an `Emulator` with a callback function, which will receive
the payloads of the tasks that you send. To send tasks, call the method `Emulator.create_task`.

# Usage Example

As a usage example, run `local_server.py`. This is a trivial webapp: Browse to http://127.0.0.1:8080 (just click the link 
in the console) and a task will be created (see `main.py`). It will be handled, on schedule, three seconds later: 
The example handler "processes" the task simply by converting it to upper case and printing it. 

This example shows how to keep the Emulator codebase separate from the production codebase. In `local_server.py`, we inject 
an `Emulator`; in deployment, where no such `Emulator` is created, a new `CloudTasksAccessor` is created that invokes
the Cloud Tasks API, keeping the server code (`main.py`) clear of any emulator code: 
You could even omit  `emulator.py` in deployment. (Though there is no harm if you leave it in.)

# Four ways to develop for Cloud Tasks
When developing code for Cloud Tasks (let's say in an HTTP server application that you are coding and debugging), 
you have four choices.
- Don't do anything
  - Write your code so that tasks are not created in development (or catch the exception and keep going).
  - Advantages:
     - This is easy and works if your main flow does not require task execution; if you are writing an application that just
     fires off tasks and has nothing more to do with them.
  - Disadvantages:
     - The tasks are never executed, so you cannot debug code that does that.
- Use the live Cloud Tasks API.
  - Advantages:
     - Full features and exact functionality of the Cloud Tasks service to be used in deployment
  - Disadvantages:
     - Requires a network connection.
     - Requires a Google Cloud project of your own and the same number of queues as are used in production. 
     If you have to share a project with other developers, you need to manage the queues so that each 
     developer gets their own set.
     - Leaves the task flow out of your debugging scope: If a task goes missing, you cannot use your debugger, but
     rather have to track it down online using Cloud Console and other GCP tools.
- Use an emulator that runs on localhost and exposes the same REST API as Cloud Tasks
  - Two are available
    - [gcloud-tasks-emulator](https://pypi.org/project/gcloud-tasks-emulator/)
    - [cloud-tasks-emulator](https://github.com/aertje/cloud-tasks-emulator)
  - Advantages:
    - Realistic emulation of the Cloud Tasks system. You do not need to change any API calls, just the endpoint.
  - Disadvantages
    - Requires you to manage another process. You have to run it before each debug session, keep track of whether it
    has crashed or frozen, and restart it as needed.
    - Difficult to debug. If you want to see why a task has not arrived, you cannot use your debugger in your main server
    process, nor can you find the task online using Cloud Console.
    - The emulation of the real Cloud Tasks system is still not perfect.
- Use an emulator that runs inside the same process as your server.
  - Advantages:
    - TODO
  - Disadvantages
    - TODO
     
# More reading
- For details on using Cloud Tasks, refer to the
 [Python sample README](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/tasks/README.md) for 
 Cloud Tasks, which was also the starting point for the sample server shown here.

