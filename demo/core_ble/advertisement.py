import dbus

from demo.constants import (
    DBUS_PROP_IFACE,
    LE_ADVERTISEMENT_IFACE,
    LE_ADVERTISING_MANAGER_IFACE,
)
from demo.exceptions import AdvertisementException, InvalidArgsException


def register_ad_cb() -> None:
    print("Advertisement registered")


# Not sure what the error type is here
def register_ad_error_cb(error) -> None:
    print(f"Failed to register advertisement: {error}")
    raise AdvertisementException()


class Advertisement(dbus.service.Object):
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
        # TODO: check if this could be empty
        self.manufacturer_data = {0xFFFF: dbus.Array([0x70, 0x74], signature="y")}
        self.data = None
        self.adapter_obj = adapter_obj
        dbus.service.Object.__init__(self, bus, self.path)

    def init_advertisement(self) -> None:
        """
        Sets up and register the advertisement for the BLE server

        Returns:
            None
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
        Releases the advertisement
        """
        self.Release()

    def get_properties(self):
        properties = dict()
        properties["Type"] = self.ad_type
        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")
        if self.solicit_uuids is not None:
            properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature="s")
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(
                self.manufacturer_data, signature="qv"
            )
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(
                self.manufacturer_data, signature="qv"
            )
        if self.service_data is not None:
            properties["ServiceData"] = dbus.Dictionary(
                self.service_data, signature="sv"
            )
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)
        if self.include_tx_power is not None:
            properties["IncludeTxPower"] = dbus.Boolean(self.include_tx_power)

        if self.data is not None:
            properties["Data"] = dbus.Dictionary(self.data, signature="yv")
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = dbus.Dictionary({}, signature="sv")
        self.service_data[uuid] = dbus.Array(data, signature="y")

    def add_data(self, ad_type, data):
        if not self.data:
            self.data = dbus.Dictionary({}, signature="yv")
        self.data[ad_type] = dbus.Array(data, signature="y")

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()

        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print(f"{self.path}: Released!")
