import enum
from multiprocessing import Process
from signal import SIGINT, SIGTERM, signal

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from demo.core_ble.advertisement import Advertisement
from demo.core_ble.application import Application
from demo.constants import BLUEZ_SERVICE_NAME, DBUS_OM_IFACE, GATT_MANAGER_IFACE
from demo.exceptions import BluetoothNotFoundException
from demo.core_ble.service import Service


def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None


def register_app_cb():
    print("Bluetooth service registered")


def register_app_error_cb(error):
    print("Failed to register application: " + str(error))


class BLEProcess(Process):
    def __init__(self) -> None:
        super().__init__()
        self._system_bus = None
        self._mainloop = None
        self._advertisement = None

    def _shutdown_handler(self, sig: enum, frame: enum) -> None:
        """
        A function that stops the main loop and stop the advertisements.
        """
        self._mainloop.quit()
        self._advertisement.release()

    def run(self) -> None:
        """
        The main run function that set-ups the BLE service.
        """

        # The mainloop initialized here handles the asynchronous communication over dbus documentation can be found
        # here: https://docs.gtk.org/glib/main-loop.html
        self._mainloop = GLib.MainLoop()

        # register shutdown handler
        signal(SIGTERM, self._shutdown_handler)
        signal(SIGINT, self._shutdown_handler)

        self._system_bus = dbus.SystemBus()
        adapter = find_adapter(self._system_bus)

        if not adapter:
            raise BluetoothNotFoundException()

        adapter_obj = self._system_bus.get_object(
            bus_name=BLUEZ_SERVICE_NAME, object_path=adapter
        )

        service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)

        # Create the advertisement
        self._advertisement = Advertisement(
            bus=self._system_bus,
            index=0,
            adapter_obj=adapter_obj,
            uuid="0000180d-aaaa-1000-8000-0081239b35fb",
            name="pycon_demo_service",
        )

        # Create the application and add the service to it
        app = Application(self._system_bus)

        example_service = Service(
            bus=self._system_bus,
            index=0,
            uuid="0000180d-aaaa-1000-8000-0081239b35fb",
            primary=True,
        )

        app.add_service(example_service)

        # Initialise the advertisement
        self._advertisement.init_advertisement()

        # Register the application
        service_manager.RegisterApplication(
            app.get_path(),
            {},
            reply_handler=register_app_cb,
            error_handler=register_app_error_cb,
        )

        # blocking call to run the main loop
        self._mainloop.run()
