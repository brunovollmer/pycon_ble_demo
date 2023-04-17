import queue

import dbus

from ble.characteristic import Characteristic
from ble.constants import DBUS_PROP_IFACE, GATT_SERVICE_IFACE
from ble.exceptions import InvalidArgsException
from ble.util import check_flags


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """

    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

        self.characteristic_queues = {}

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "characteristics": dbus.Array(
                    self.get_characteristic_paths(), signature="o"
                ),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, uuid, flags, description, default_value):
        check_flags(flags)

        self.characteristic_queues[uuid] = queue.Queue()

        characteristic = Characteristic(
            self.bus,
            len(self.characteristics),
            uuid,
            flags,
            self,
            description,
            default_value,
            self.characteristic_queues[uuid],
        )

        self.characteristics.append(characteristic)

    def write_to_characteristic(self, value, uuid):
        # TODO check size of value and raise exception if too big
        self.characteristic_queues[uuid].put(value)

    def get_characteristic_paths(self):
        result = []
        for characteristic in self.characteristics:
            result.append(characteristic.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]
