# In-Process Simple Emulator for Google Cloud Tasks
Google [doesn't](https://cloud.google.com/tasks/docs/migrating#features_in_task_queues_not_yet_available_via)
[offer](https://issuetracker.google.com/issues/133627244)
an emulator for the Cloud Tasks API,  as it does for Datastore or PubSub. This project answers that need.

# Article
See the article at the [DoiT](https://blog.doit-intl.com) for full details.

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
- The example handler "processes" the task simply by upper-casing it and printing it.
- This example shows how to keep the Emulator codebase separate from the production codebase. 
  - In `local_server.py` used in development, we inject an `Emulator`.
  - In contrast , in a deployed server, where no such `Emulator` is injected, a new `CloudTasksAccessor` is created that invokes
  the real Cloud Tasks API, keeping the server code (`main.py`) clear of any emulator code.
  - For full separation, you could even omit  `emulator.py` in deployment. (Though there is no harm if you leave it in.)
- To deploy this example  app, run ` gcloud -q app deploy app.yaml`

# Alternative approaches

For developing with Cloud Tasks, your choices are:
- Use the real Cloud Tasks, using ngrok to expose your dev machine for callbacks.
- Skipping Cloud Tasks in development
- An emulator that runs in localhost
- An in-process emulator like like this one.

See the article mentioned above for details.
    
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
