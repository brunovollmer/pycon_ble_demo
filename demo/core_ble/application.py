from typing import Dict

import dbus

from demo.core_ble.constants import DBUS_OM_IFACE
from demo.core_ble.service import Service


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation.
    """

    def __init__(self, system_bus: dbus.SystemBus) -> None:
        """
        Constructor of application class. Set own path and initialize services variable.

        Args:
            system_bus (dbus.SystemBus): system bus object
        """
        self.path = "/"
        self.services = []

        dbus.service.Object.__init__(self, system_bus, self.path)

    def get_path(self) -> str:
        """
        Get dbus object path for given input path.

        Returns:
            str: dbus object path
        """
        return dbus.ObjectPath(self.path)

    def add_service(self, service: Service) -> None:
        """
        Add service to application.

        Args:
            service (Service): service to add
        """
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self) -> Dict[str, dbus.ObjectPath]:
        """
        Overwrite GetManagedObjects to add all characteristics of the added services.

        Returns:
            Dict[str, dbus.ObjectPath]: all managed objects of this application
        """
        response = {}

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            characteristics = service.get_characteristics()
            for characteristic in characteristics:
                response[characteristic.get_path()] = characteristic.get_properties()
                descriptors = characteristic.get_descriptors()
                for descriptor in descriptors:
                    response[descriptor.get_path()] = descriptor.get_properties()

        return response
