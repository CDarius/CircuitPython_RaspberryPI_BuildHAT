# CircuitPython library for RaspberryPI Build HAT

![1725627821628](https://github.com/user-attachments/assets/2ece3282-8bec-4612-8e6b-cf24a7662934)

This is a CircuitPython library that let you control Lego devices (motors, distance sensors, color sensors, etc...) through the [RaspberryPI Build HAT](https://www.raspberrypi.com/documentation/accessories/build-hat.html).
Connect a CircuitPython device to the RaspberryPI Build HAT require just 4 for wire:

| CircuitPython board | Build HAT |
| :------------------:|:---------:|
| Serial TX           |  GPIO 14  |
| Serial RX           |  GPIO 15  |
| Digital output (reset)      |  GPIO 4   |
| GND                 |  GND      |

It is also possible to use the 5V from the Build HAT to power the CircuitPython board.

> The first time that the Build HAT library starts need to load the firmware in the HAT. It takes about 30 seconds to load the firmware and restart the HAT. Please wait until the firmware is loaded

# Simple example
The following code initialize the Build HAT (load the firmware) and list the connected Lego devices
```python
import board
from buildhat.hat import Hat

# Change the pins to match your board wiring
tx_pin = board.TX
rx_pin = board.RX
reset_pin = board.GP23

buildhat = Hat(tx=tx_pin, rx=rx_pin, reset=reset_pin, debug=True)
for port in range(4):
    device = buildhat.get_device(port)
    if device:
        print(f"Port {port}: {device.name}")
```

# Attribution
In order to develop this library I used as a reference the official [RaspberryPI Python library](https://github.com/RaspberryPiFoundation/python-build-hat) and the [.NET library](https://github.com/dotnet/iot/blob/main/src/devices/BuildHat/README.md)
The firmware in the [data directory](buildhat/data) comes from the RaspberryPI [Build HAT repo](https://github.com/RaspberryPiFoundation/python-build-hat/tree/main/buildhat/data)
