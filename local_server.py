import main
from cloud_tasks_emulator.emulator import Emulator

if __name__ == '__main__':
   # main.cloud_tasks_client = Emulator(task_handler=main.handle_task)
    main.app.run(host='127.0.0.1', port=8080, debug=True)
