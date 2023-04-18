from typing import Dict, Union

import dbus

from demo.core_ble.constants import (
    DBUS_PROP_IFACE,
    LE_ADVERTISEMENT_IFACE,
    LE_ADVERTISING_MANAGER_IFACE,
)
from demo.exceptions import AdvertisementException, InvalidArgsException


def register_ad_cb():
    """
    Callback for when the advertisement is registered.
    """

    print("Advertisement registered")


def register_ad_error_cb(error: dbus.DBusException):
    """
    Callback for when there is an error registering the advertisement.

    Args:
        error (dbus.DBusException): error that occurred

    Raises:
        AdvertisementException: raised when there is an error registering the advertisement
    """

    print(f"Failed to register advertisement: {error}")
    raise AdvertisementException()


class Advertisement(dbus.service.Object):
    """
    org.bluez.LEAdvertisement1 interface implementation
    """

    PATH_BASE = "/org/bluez/pycon_demo/advertisement"

    def __init__(self, bus, index, adapter_obj, uuid, name):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = "peripheral"
        self.service_uuids = [uuid]
        self.solicit_uuids = None
        self.service_data = None
        self.local_name = dbus.String(name)
        self.include_tx_power = None
        self.manufacturer_data = {0xFFFF: dbus.Array([0x70, 0x74], signature="y")}
        self.data = None
        self.adapter_obj = adapter_obj
        dbus.service.Object.__init__(self, bus, self.path)

    def init_advertisement(self):
        """
        Sets up and register the advertisement for the GATT server.
        """
        ad_manager = dbus.Interface(self.adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

        ad_manager.RegisterAdvertisement(
            self.get_path(),
            {},
            reply_handler=register_ad_cb,
            error_handler=register_ad_error_cb,
        )

    def release(self) -> None:
        """
        Releases the advertisement.
        """
        self.Release()

    def get_properties(self) -> Dict[str, Union[dbus.Array, dbus.Boolean, dbus.Dictionary]]:
        """
        Create the dbus properties of the advertisement object.

        Returns:
            Dict[str, Union[dbus.Array, dbus.Boolean, dbus.Dictionary]]: properties of the advertisement
        """
        properties = dict()
        properties["Type"] = self.ad_type

        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")
        if self.solicit_uuids is not None:
            properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature="s")
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(self.manufacturer_data, signature="qv")
        if self.service_data is not None:
            properties["ServiceData"] = dbus.Dictionary(self.service_data, signature="sv")
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)
        if self.include_tx_power is not None:
            properties["IncludeTxPower"] = dbus.Boolean(self.include_tx_power)
        if self.data is not None:
            properties["Data"] = dbus.Dictionary(self.data, signature="yv")

        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self) -> dbus.ObjectPath:
        """
        Return the object path of the advertisement.

        Returns:
            dbus.ObjectPath: dbus path
        """
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface: str) -> Dict[str, Union[dbus.Array, dbus.Boolean, dbus.Dictionary]]:
        """
        Get all properties of the advertisement DBUS function.

        Args:
            interface: name of interface

        Raises:
            InvalidArgsException: wrong interface name

        Returns:
            Dict[str, Union[dbus.Array, dbus.Boolean, dbus.Dictionary]]
        """
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        """
        Release the advertisement DBUS function.
        """

        print(f"{self.path}: Released!")
