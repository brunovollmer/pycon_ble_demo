import dbus
import multiprocessing
import queue
import time

from demo.ble_process import BLEProcess

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


def main():
    output_queue = multiprocessing.Queue()
    
    ble_process = BLEProcess(output_queue)
    ble_process.start()

    while True:
        try:
            curr_value = output_queue.get(timeout=1)
            print(f"Value written to Characteristic with UUID {curr_value['uuid']}: {curr_value['value']}")
        except queue.Empty:
            time.sleep(1)
        



if __name__ == "__main__":
    main()
