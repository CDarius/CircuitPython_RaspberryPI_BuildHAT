class DeviceType:
    # None
    NONE = 0

    # System medium motor
    SYSTEM_MEDIUM_MOTOR = 1

    # System train motor
    SYSTEM_TRAIN_MOTOR = 2

    # System turntable motor
    SYSTEM_TURNABLE_MOTOR = 3

    # General PWM/third party
    GENERAL_PWM = 4

    # Button/touch sensor
    BUTTON_OR_TOUCH_SENSOR = 5

    # Simple lights
    SIMPLE_LIGHTS = 8

    # Future lights 1
    FUTURE_LIGHTS_1 = 9

    # Future lights 2
    FUTURE_LIGHTS_2 = 10

    # System future actuator (train points)
    SYSTEM_FUTURE_ACTUATOR = 11

    # Following ones are active

    # WeDo tilt sensor
    WEDO_TILT_SENSOR = 0x22

    # WeDo motion sensor
    WEDO_MOTION_SENSOR = 0x23

    # Colour and distance sensor
    COLOR_AND_DISTANCE_SENSOR = 0x25

    # Medium linear motor
    MEDIUM_LINEAR_MOTOR = 0x26

    # Technic large motor
    TECHNIC_LARGE_MOTOR = 0x2E

    # Technic XL motor
    TECHNIC_XL_MOTOR = 0x2F

    # SPIKE Prime medium motor
    SPIKE_MEDIUM_ANGULAR_MOTOR = 0x30

    # SPIKE Prime large motor
    SPIKE_LARGE_ANGULAR_MOTOR = 0x31

    # SPIKE Prime colour sensor
    SPIKE_COLOR_SENSOR = 0x3D

    # SPIKE Prime ultrasonic distance sensor
    SPIKE_ULTRASONIC_DISTANCE_SENSOR = 0x3E

    # SPIKE Prime force sensor
    SPIKE_FORCE_SENSOR = 0x3F

    # SPIKE Essential 3x3 colour light matrix
    SPIKE_3X3_COLOR_LIGHT_MATRIX = 0x40

    # SPIKE Essential small angular motor
    SPIKE_SMALL_ANGULAR_MOTOR = 0x41

    # Technic medium motor
    TECHNIC_MEDIUM_ANGULAR_MOTOR = 0x4B

    # Technic large motor
    TECHNIC_LARGE_ANGULAR_MOTOR = 0x4C

    def get_name(type_id: int) -> str:
        if type_id == DeviceType.NONE:
            return "None"
        elif type_id == DeviceType.SYSTEM_MEDIUM_MOTOR:
            return "System medium motor"
        elif type_id == DeviceType.SYSTEM_TRAIN_MOTOR:
            return "System train motor"
        elif type_id == DeviceType.SYSTEM_TURNABLE_MOTOR:
            return "System turntable motor"
        elif type_id == DeviceType.GENERAL_PWM:
            return "General PWM/third party"
        elif type_id == DeviceType.BUTTON_OR_TOUCH_SENSOR:
            return "Button/touch sensor"
        elif type_id == DeviceType.SIMPLE_LIGHTS:
            return "Lights"
        elif type_id == DeviceType.FUTURE_LIGHTS_1:
            return "Future lights 1"
        elif type_id == DeviceType.FUTURE_LIGHTS_2:
            return "Future lights 2"
        elif type_id == DeviceType.SYSTEM_FUTURE_ACTUATOR:
            return "System future actuator (train points)"
        elif type_id == DeviceType.WEDO_TILT_SENSOR:
            return "WeDo tilt sensor"
        elif type_id == DeviceType.WEDO_MOTION_SENSOR:
            return "WeDo motion sensor"
        elif type_id == DeviceType.COLOR_AND_DISTANCE_SENSOR:
            return "Colour and distance sensor"
        elif type_id == DeviceType.MEDIUM_LINEAR_MOTOR:
            return "Medium linear motor"
        elif type_id == DeviceType.TECHNIC_LARGE_MOTOR:
            return "Technic large motor"
        elif type_id == DeviceType.TECHNIC_XL_MOTOR:
            return "Technic XL motor"
        elif type_id == DeviceType.SPIKE_MEDIUM_ANGULAR_MOTOR:
            return "SPIKE medium motor"
        elif type_id == DeviceType.SPIKE_LARGE_ANGULAR_MOTOR:
            return "SPIKE large motor"
        elif type_id == DeviceType.SPIKE_COLOR_SENSOR:
            return "SPIKE colour sensor"
        elif type_id == DeviceType.SPIKE_ULTRASONIC_DISTANCE_SENSOR:
            return "SPIKE ultrasonic distance sensor"
        elif type_id == DeviceType.SPIKE_FORCE_SENSOR:
            return "SPIKE force sensor"
        elif type_id == DeviceType.SPIKE_3X3_COLOR_LIGHT_MATRIX:
            return "SPIKE 3x3 colour light matrix"
        elif type_id == DeviceType.SPIKE_SMALL_ANGULAR_MOTOR:
            return "SPIKE small angular motor"
        elif type_id == DeviceType.TECHNIC_MEDIUM_ANGULAR_MOTOR:
            return "Technic medium angular motor"
        elif type_id == DeviceType.TECHNIC_LARGE_ANGULAR_MOTOR:
            return "Technic large angular motor"
        else:
            return "Unknown"

    def is_motor(type_id: int) -> bool:
        return type_id in _ALL_MOTORS


_ALL_MOTORS = (
    DeviceType.SYSTEM_MEDIUM_MOTOR,
    DeviceType.SYSTEM_TRAIN_MOTOR,
    DeviceType.SYSTEM_TURNABLE_MOTOR,
    DeviceType.MEDIUM_LINEAR_MOTOR,
    DeviceType.TECHNIC_LARGE_MOTOR,
    DeviceType.TECHNIC_XL_MOTOR,
    DeviceType.SPIKE_MEDIUM_ANGULAR_MOTOR,
    DeviceType.SPIKE_LARGE_ANGULAR_MOTOR,
    DeviceType.SPIKE_SMALL_ANGULAR_MOTOR,
    DeviceType.TECHNIC_MEDIUM_ANGULAR_MOTOR,
    DeviceType.TECHNIC_LARGE_ANGULAR_MOTOR,
)
