# In-Process Simple Emulator for Google Cloud Tasks
Google doesn't (yet) ship an emulator for the Cloud Tasks API like they do for
Cloud Datastore.

# Usage
To use this emaulator, copy `emulator.py` into your codebase.

Invoke it by TODO

As a usage example, see `main.py`. In development, set the `GAE_APPLICATION` environment variable when running it, available
with  `gcloud config get-value project`


# More reading
- For details on using Cloud Tasks, refer to the [Python sample README](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/tasks/README.md) Cloud Tasks 
- For an emulator that runs on localhost and exposes the same REST API as Cloud Tasks, see  [gcloud-tasks-emulator](https://pypi.org/project/gcloud-tasks-emulator/)

