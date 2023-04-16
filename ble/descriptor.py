import dbus
import array

from ble.constants import GATT_DESC_IFACE, DBUS_PROP_IFACE
from ble.exceptions import InvalidArgsException
from ble.util import str_to_byte_arr


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """

    def __init__(self, bus, index, characteristic, description):
        self.path = characteristic.path + "/desc" + str(index)
        self.bus = bus
        # TODO: why 2901?
        self.uuid = "2901"
        self.flags = ['read']
        self.characteristic = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

        self.value = str_to_byte_arr(description)

    def get_properties(self):
        return {
            GATT_DESC_IFACE: {
                "Characteristic": self.characteristic.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        return self.value
