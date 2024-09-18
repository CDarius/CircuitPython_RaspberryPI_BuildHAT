.. If you created a package, create one automodule per module in the package.

.. If your library file(s) are nested in a directory (e.g. /adafruit_foo/foo.py)
.. use this format as the module name: "adafruit_foo.foo"

Hat
===

.. automodule:: buildhat.hat
    :members:
    :inherited-members:

Devices
=======

.. autoclass:: buildhat.device::Device()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.activedevice::ActiveDevice()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.devices.colordistancesensor.ColorDistanceSensor()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.devices.colorsensor.ColorSensor()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.devices.lightmatrix.LightMatrix()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.devices.ultrasonicdistancesensor.UltrasonicDistanceSensor()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

Motors
======

.. autoclass:: buildhat.motors.passivemotor.PassiveMotor()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

.. autoclass:: buildhat.motors.activemotor.ActiveMotor()
    :members:
    :inherited-members:
    :exclude-members: on_disconnect, hat, on_combi_value_update, on_single_value_update

    .. py:property:: hat
        :type: buildhat.hat.Hat

        Return a Build HAT instace

Enums
=====

.. automodule:: buildhat.models.devicetype
    :members:
    :member-order: bysource

.. autoclass:: buildhat.motors.speedunit.SpeedUnit()
    :members:
    :member-order: bysource

.. autoclass:: buildhat.devices.color.Color()
    :members:
    :member-order: bysource

.. autoclass:: buildhat.devices.matrixcolor.MatrixColor()
    :members:
    :member-order: bysource

.. autoclass:: buildhat.devices.matrixtransition.MatrixTransition()
    :members:
    :member-order: bysource
