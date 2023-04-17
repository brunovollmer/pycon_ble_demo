import dbus

from demo.ble_process import BLEProcess

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


def main():
    ble_process = BLEProcess()
    ble_process.start()

    ble_process.join()


if __name__ == "__main__":
    main()
