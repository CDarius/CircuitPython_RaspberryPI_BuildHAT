Introduction
============

.. image:: https://readthedocs.org/projects/circuitpython-raspberrypi-buildhat/badge/?version=latest
    :target: https://circuitpython-raspberrypi-buildhat.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/CDarius/CircuitPython_RaspberryPi_BuildHAT/workflows/Build%20CI/badge.svg
    :target: https://github.com/CDarius/CircuitPython_RaspberryPi_BuildHAT/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython driver for RaspberryPi BuildHAT

.. image:: https://github.com/CDarius/CircuitPython_RaspberryPI_BuildHAT/blob/main/docs/images/video_preview.png?raw=true
    :target: https://youtu.be/DlgysdjXWgY?si=tdnGjpXb8YGwaNOh
    :alt: Preview YouTube video

Attribution
===========

In order to develop this library I used as a reference the official `RaspberryPI Python library <https://github.com/RaspberryPiFoundation/python-build-hat>`_ and the `.NET library <https://github.com/dotnet/iot/blob/main/src/devices/BuildHat/README.md>`_.
The firmware in the directory ``buildhat/data`` comes from the RaspberryPI `Build HAT repo <https://github.com/RaspberryPiFoundation/python-build-hat/tree/main/buildhat/data>`_

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `AsyncIO <https://github.com/adafruit/Adafruit_CircuitPython_asyncio>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-raspberrypi-buildhat/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-raspberrypi-buildhat

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-raspberrypi-buildhat

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-raspberrypi-buildhat

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install raspberrypi_buildhat

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

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

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-raspberrypi-buildhat.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/CDarius/CircuitPython_RaspberryPi_BuildHAT/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
