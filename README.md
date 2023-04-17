# BLE and Python - PyConDE 2023 Code Example 

This repository holds the code used in the talk "BLE and Python - How to build a simple BLE project on Linux with Python"
at PyConDE 2023.

The example code is tested with Python 3.8 and Bluez 5.65.


## Running the example

To run the code just run:
```
pip install -r requirements.txt
python main.py
```

You can now use an external app or tool on another machine to check if you can see the device under "pycon_ble_demo".

## Debugging

All of the following commands have to be run in parallel in a separate terminal window on the same machine.

To see all DBUS commands you can run the following command:
```
sudo dbus-monitor --system "destination='org.bluez'" "sender='org.bluez'"
```

To see the HCI traces of all messages you can run:
```
sudo btmon
```

## Contributing

I'm happy if you have ideas or suggestions on how to improve this little example. Please open either an issue or a pull-request for this.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for more information.

Copyright (c) 2023 Bruno Vollmer.