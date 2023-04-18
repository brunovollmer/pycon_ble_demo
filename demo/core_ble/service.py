import queue
from typing import Any, Dict, List

import dbus

from demo.core_ble.characteristic import Characteristic
from demo.core_ble.constants import DBUS_PROP_IFACE, GATT_SERVICE_IFACE
from demo.exceptions import InvalidArgsException
from demo.util import check_flags


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """

    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, bus, index, uuid, primary, output_queue):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

        self.characteristic_queues = {}
        self.output_queue = output_queue

    def get_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the properties of the service.

        Returns:
            Dict[str, Dict[str, Any]]: The properties of the service.
        """
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "characteristics": dbus.Array(self.get_characteristic_paths(), signature="o"),
            }
        }

    def get_path(self) -> dbus.ObjectPath:
        """
        Returns the path of the service.

        Returns:
            dbus.ObjectPath: The path of the service.
        """
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, uuid: str, flags: List[str], description: str, default_value: Any):
        """
        Adds a characteristic to the service.

        Args:
            uuid (str): The UUID of the characteristic.
            flags (List[str]): The flags of the characteristic.
            description (str): The description of the characteristic.
            default_value (Any): The default value of the characteristic.
        """
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
            self.output_queue,
        )

        self.characteristics.append(characteristic)

    def write_to_characteristic(self, value: Any, uuid: str):
        """
        Writes a value to a specified characteristic.

        Args:
            value (Any): The value to write to the characteristic.
            uuid (str): The UUID of the characteristic to write to.
        """
        self.characteristic_queues[uuid].put(value)

    def get_characteristic_paths(self) -> List[dbus.ObjectPath]:
        """
        Returns the paths of the characteristics.

        Returns:
            List[dbus.ObjectPath]: The paths of the characteristics.
        """
        result = []
        for characteristic in self.characteristics:
            result.append(characteristic.get_path())
        return result

    def get_characteristics(self) -> List[Characteristic]:
        """
        Returns the characteristics of the service.

        Returns:
            List[Characteristic]: The characteristics of the service.
        """
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface) -> Dict[str, Any]:
        """
        Returns all the properties of the service.

        Args:
            interface (str): The interface of the service.

        Raises:
            InvalidArgsException: If the interface is not the GATT service interface.

        Returns:
            Dict[str, Any]: All the properties of the service.
        """
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]
