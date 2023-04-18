from typing import Any, Dict

import dbus

from demo.core_ble.constants import DBUS_PROP_IFACE, GATT_DESC_IFACE
from demo.exceptions import InvalidArgsException
from demo.util import str_to_byte_arr


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """

    def __init__(self, bus, index, characteristic, description):
        self.path = characteristic.path + "/desc" + str(index)
        self.bus = bus
        self.uuid = "2901"
        self.flags = ["read"]
        self.characteristic = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

        self.value = str_to_byte_arr(description)

    def get_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the properties of the descriptor.

        Returns:
            Dict[str, Dict[str, Any]]: The properties of the descriptor.
        """
        return {
            GATT_DESC_IFACE: {
                "Characteristic": self.characteristic.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self) -> dbus.ObjectPath:
        """
        Returns the path of the descriptor.

        Returns:
            dbus.ObjectPath: The path of the descriptor.
        """
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface) -> Dict[str, Any]:
        """
        Returns all the properties of the descriptor.

        Args:
            interface (str): The interface of the descriptor.

        Raises:
            InvalidArgsException: If the interface is not the GATT descriptor interface.

        Returns:
            Dict[str, Any]: All the properties of the descriptor.
        """

        if interface != GATT_DESC_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options) -> Any:
        """
        Returns the value of the descriptor.

        Args:
            options (Dict[str, Any]): A dictionary of options.

        Returns:
            Any: The value of the descriptor.
        """
        return self.value
