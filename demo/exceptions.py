import dbus.exceptions


class InvalidArgsException(dbus.exceptions.DBusException):
    """
    Invalid arg exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class BluetoothNotFoundException(Exception):
    """
    This exception is thrown when an error with the Gatt service occurs, usually this happens when Bluetooth is off
    """

    def __init__(
        self,
    ):
        super().__init__("Bluetooth service was not found, your Bluetooth is most likely off")


class AdvertisementException(Exception):
    """
    This exception is thrown when an error with advertisement occurs, it usually suffices to restart the
    Bluetooth Service

    """

    def __init__(self):
        super().__init__("Advertisement Registration Error occurred")
