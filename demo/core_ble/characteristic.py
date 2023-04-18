import queue
from typing import Any, Dict, List

import dbus
from gi.repository import GObject

from demo.core_ble.constants import DBUS_PROP_IFACE, GATT_CHRC_IFACE
from demo.core_ble.descriptor import Descriptor
from demo.exceptions import InvalidArgsException
from demo.util import byte_arr_to_str, str_to_byte_arr


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation.
    """

    def __init__(self, bus, index, uuid, flags, service, description, default_value, input_queue, output_queue):
        self.path = service.path + "/char" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = [Descriptor(bus, 0, self, description)]

        dbus.service.Object.__init__(self, bus, self.path)

        self.value = str_to_byte_arr(default_value)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.notification_timeout_id = None

        if "notify" in self.flags:
            self.notifying = True
        else:
            self.notifying = False

    def get_properties(self) -> Dict[str, Dict[str, Any]]:
        """ "
        Returns a dictionary of all the properties of the characteristic.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary of all the properties of the characteristic.
        """

        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
                "Descriptors": dbus.Array(self.get_descriptor_paths(), signature="o"),
            }
        }

    def input_queue_callback(self):
        """
        Callback function for the input queue. This function is called every 10ms to check if there is a new value in the input queue.
        If there is a new value, it is written to the characteristic and a PropertiesChanged signal is emitted.
        """

        try:
            curr_value = self.input_queue.get(False)
        except queue.Empty:
            return self.notifying

        self.value = str_to_byte_arr(str(curr_value))
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": self.value}, [])

    def get_path(self) -> dbus.ObjectPath:
        """ "
        Returns the path of the characteristic.

        Returns:
            dbus.ObjectPath: The path of the characteristic.
        """
        return dbus.ObjectPath(self.path)

    def get_descriptor_paths(self) -> List[dbus.ObjectPath]:
        """
        Returns a list of all the paths of the descriptors of the characteristic.

        Returns:
            List[dbus.ObjectPath]: A list of all the paths of the descriptors of the characteristic.
        """
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self) -> List[Descriptor]:
        """
        Returns a list of all the descriptors of the characteristic.

        Returns:
            List[Descriptor]: A list of all the descriptors of the characteristic.
        """
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface) -> Dict[str, Any]:
        """
        Returns a dictionary of all the properties of the characteristic.

        Args:
            interface (str): The interface of the characteristic.

        Returns:
            Dict[str, Any]: A dictionary of all the properties of the characteristic.
        """
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options: Dict[str, Any]) -> Any:
        """
        Returns the value of the characteristic.

        Args:
            options (Dict[str, Any]): A dictionary of options.

        Returns:
            Any: The value of the characteristic.
        """
        return self.value

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value: Any, options: Dict[str, Any]):
        """
        Writes a value to the characteristic.
        """
        self.value = value
        self.output_queue.put({"uuid": self.uuid, "value": byte_arr_to_str(value)})

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        """
        Set the characteristic to notifying.
        """
        if self.notifying:
            return

        self.notifying = True
        self.notification_timeout_id = GObject.timeout_add(10, self.input_queue_callback)

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        """
        Set the characteristic to not notifying.
        """

        self.notifying = False
        GObject.source_remove(self.notification_timeout_id)
