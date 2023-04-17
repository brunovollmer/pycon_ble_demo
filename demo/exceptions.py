import dbus.exceptions


class InvalidArgsException(dbus.exceptions.DBusException):
    """
    Invalid arg exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    """
    NotSupportedException exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    """
    NotPermittedException exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    """
    InvalidValueLengthException exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    """
    FailedException exception dbus uses for BLE communication

    """

    _dbus_error_name = "org.bluez.Error.Failed"


class BluetoothNotFoundException(Exception):
    """
    This exception is thrown when an error with the Gatt service occurs, usually this happens when Bluetooth is off
    """

    def __init__(
        self,
        message="Bluetooth service was not found, your Bluetooth is most likely off",
    ):
        self.message = message
        super().__init__(self.message)


class AdvertisementException(Exception):
    """
    This exception is thrown when an error with advertisement occurs, it usually suffices to restart the
    Bluetooth Service

    """

    def __init__(self, message="Advertisement Registration Error occurred"):
        self.message = message
        super().__init__(self.message)
