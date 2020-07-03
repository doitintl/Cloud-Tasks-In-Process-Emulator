# In-Process Simple Emulator for Google Cloud Tasks
Google [doesn't](https://cloud.google.com/tasks/docs/migrating#features_in_task_queues_not_yet_available_via)
[offer](https://issuetracker.google.com/issues/133627244)
an emulator for the Cloud Tasks API,  as it does for Datastore or PubSub. This project answers that need.

# Usage

To use this emulator
- Copy `emulator.py` into your codebase. 
- Create an `Emulator` object, passing a callback function, which will receive
the payloads of the tasks that you create. 
- To send tasks, call the method `Emulator.create_task`. You can choose the queue and the scheduled delivery time.

# Usage Example

- As a usage example, run `local_server.py`. 
- This is a trivial webapp: Browse to [http://127.0.0.1:8080](http://127.0.0.1:8080) 
(or just click the link 
in the console) and a task will be created (see `main.py`). 
- It will be handled, on schedule, three seconds later.
- The example handler "processes" the task simply by converting it to upper case and printing it.
- This example shows how to keep the Emulator codebase separate from the production codebase. 
  - In `local_server.py` used in development, we inject an `Emulator`.
  - In contrast , in a deployed server, where no such `Emulator` is injected, a new `CloudTasksAccessor` is created that invokes
  the real Cloud Tasks API, keeping the server code (`main.py`) clear of any emulator code.
  - For full separation, you could even omit  `emulator.py` in deployment. (Though there is no harm if you leave it in.)
- To deploy this example  app, run ` gcloud app deploy app.yaml`

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
     - Works with code in any language.
  - Disadvantages:
     - Tou will need to set up a proxy like ngrok to receive tasks:
     [See the article](https://medium.com/google-cloud/develop-your-cloud-tasks-pipeline-locally-with-ngrok-5bee3693600f)
     - Requires a network connection.
     - Requires a Google Cloud project of your own and the same number of queues as are used in production. 
     If you have to share a project with other developers, you need to manage the queues so that each 
     developer gets their own set.
     - Leaves the task flow out of your debugging scope: If a task goes missing, you cannot use your debugger, but
     rather have to track it down online using Cloud Console and other GCP tools.

- Use an emulator that runs on localhost and exposes the same REST API as Cloud Tasks
  - Two are available
    - Potato London's [gcloud-tasks-emulator](https://pypi.org/project/gcloud-tasks-emulator/), in Python.
    - Aert van de Hulsbeek's [cloud-tasks-emulator](https://github.com/aertje/cloud-tasks-emulator), in Go.
  - Advantages:
    - Realistic emulation of the Cloud Tasks system. You do not need to change any API calls, just the endpoint.
     - Works with code in any language.
  - Disadvantages
    - Requires you to manage another process. You have to run it before each debug session, keep track of whether it
    has crashed or frozen, and restart it as needed.
    - Difficult to debug. If you want to see why a task has not arrived, you cannot use your debugger in your main server
    process, nor can you find the task online using Cloud Console.
    - The emulation of the real Cloud Tasks system is still not perfect.
    - The available emulators are in alpha release.
- Wrap the PubSub emulator (which runs on localhost)
  - Advantages:
    - This is a robust emulator.
    - Functionality similar to Cloud Task.
    - Works with code in any language (other than the client-side wrapper).
  - Disadvantages
    - You still need to maintain a separate process on your machine.
    - The functionality is not really the same as Cloud Tasks; e.g., no scheduling.
    - The API is not the same, so you can't just swap endpoints to use your emulato.
    You'll have to write a wrapper.
- Use an emulator that runs inside the same process as your server, as for example the one
in this project.
  - Advantages:
    - You can track each message using your debugger.
    - No separate component to manage.
    - The available emulators are all in alpha release: The two localhost emulators, and my own 
    in-process emulator. It's easier to deal with that if you have full control of the code, running
    it in your debugger and tweaking the code for your purposes.
  - Disadvantages
    - Not fully transparent: You will have to wrap the code so you can call either the emulator
    or the real Cloud Tasks API.
    - Only works with the one language in which the emulator is written; in the case of this , Python.
    - Not fully realistic: The tasks do not travel the network.
    - Some functionality is missing (at least in my implementation).
    
# Scope of functionality
  - This project supports the functionality that you typically use in development: Creating
  a task, and then handling the task in a callback.
  - Some unsupported features:
    - Queue management, including creating, deleting, purging, pausing and resuming queues.
    (When you add a task, a queue is automatically created if not yet present for that task.)
    - Configuration of rate limits and retries.
    - Deduplication and deletion of tasks.
  - These features could be added, but:
    - I believe that a simpler codebase is better for the debugging scenario; as-is, the whole
     emulator is  under 100 lines and easy to understand. 
     For fuller functionality and more realistic testing, I would use the real Cloud Tasks, 
     in a deployed system.
  - If you would like improvements, please submit Pull Requests or Issues.

# More reading
- For details on using Cloud Tasks, refer to the
 [Python sample README](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/tasks/README.md) for 
 Cloud Tasks, which was also the starting point for the sample server shown here.

