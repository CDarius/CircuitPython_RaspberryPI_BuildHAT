List all connected devices
--------------------------

Ensure your device works with this simple test that initialize the Build HAT and list all the connected devices

.. literalinclude:: ../examples/simpletest.py
    :caption: examples/simpletest.py
    :linenos:

Active motor
------------

Run a motor in the different modes: relative, absolute, position and with different
speed measuring unit: degrees per second, revoluitions per minutes

.. literalinclude:: ../examples/active_motor.py
    :caption: examples/active_motor.py
    :linenos:

Color sensor
------------

Reads all the measurable values: color, ambient light, reflected light
It also show how to switch off and on the sensor

.. literalinclude:: ../examples/color_sensor.py
    :caption: examples/color_sensor.py
    :linenos:

Color + distance sensor
-----------------------

Reads all the measurable values: color, ambient light, reflected light, distance, counter
It also show how to switch off and on the sensor

.. literalinclude:: ../examples/color_distance_sensor.py
    :caption: examples/color_distance_sensor.py
    :linenos:

Ultrasonic distance sensor
--------------------------

Use several tasks to continuosly read the distance and animate the eyes lights

.. literalinclude:: ../examples/distance_sensor.py
    :caption: examples/distance_sensor.py
    :linenos:

3x3 Color Light matrix
----------------------

Show how to drive the display in the different mode and how to apply transitions

.. literalinclude:: ../examples/light_matrix.py
    :caption: examples/light_matrix.py
    :linenos:
