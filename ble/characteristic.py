import queue

import dbus
from gi.repository import GObject

from ble.constants import DBUS_PROP_IFACE, GATT_CHRC_IFACE, GATT_DESC_IFACE
from ble.descriptor import Descriptor
from ble.exceptions import InvalidArgsException, NotSupportedException
from ble.util import str_to_byte_arr


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation. This class is used to be overwritten by our implementations
    of the different characteristics.
    """

    def __init__(
        self, bus, index, uuid, flags, service, description, default_value, input_queue
    ):
        self.notifying = None
        self.notification_timeout_id = None
        self.path = service.path + "/char" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = [Descriptor(bus, 0, self, description)]
        dbus.service.Object.__init__(self, bus, self.path)

        self.value = str_to_byte_arr(default_value)
        self.input_queue = input_queue

        if "notify" in self.flags:
            self.notifying = True
        else:
            self.notifying = False

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
            }
        }

    def input_queue_callback(self):
        try:
            curr_value = self.input_queue.get(False)
        except queue.Empty:
            return self.notifying

        self.value = str_to_byte_arr(str(curr_value))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.value}, [])

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    def _handle_notification(self):
        pass
        # TODO

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        return self.value

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        self.value = value

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        self.notification_timeout_id = GObject.timeout_add(
            10, self.input_queue_callback
        )

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        self.notifying = False
        GObject.source_remove(self.notification_timeout_id)

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass
