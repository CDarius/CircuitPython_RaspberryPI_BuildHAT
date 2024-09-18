# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT

"""
Example that initialize the Build HAT and list all the connected devices
Having debug=True it also print in the output console all steps during hat initialization
"""

import board

from buildhat.hat import Hat

# Pins for Waveshare RP2040-Zero.
# Change the pins if you are using a different board
tx_pin = board.TX
rx_pin = board.RX
reset_pin = board.GP23

buildhat = Hat(tx=tx_pin, rx=rx_pin, reset=reset_pin, debug=True)
for port in range(4):
    device = buildhat.get_device(port)
    if device:
        print(f"Port {port}: {device.name}")
