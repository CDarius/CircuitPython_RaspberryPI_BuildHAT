import sys
import traceback

import buildhat.hat
from .device import Device
from .models.combimodes import CombiModes
from .models.devicetype import DeviceType
from .models.modedetails import ModeDetails
from .models.minmaxvalue import MinMaxValue
from .models.modetypevalue import ModeTypeValue

try:
    from typing import Dict, List
except:
    pass

_DETAILS_TYPE_ACTIVE = "type "
_DETAILS_N_MODES = "  nmodes ="
_DETAILS_BAUD = "  baud   ="
_DETAILS_HARDWARE_VERSION = "  hwver  ="
_DETAILS_SOFTWARE_VERSION = "  swver  ="
_DETAILS_FORMAT_COUNT = "    format "
_DETAILS_UNIT = " SI = "


class ActiveDevice(Device):
    def __init__(self, hat: buildhat.hat.Hat, port: str, type: DeviceType):
        super().__init__(hat, port, type)

        self._baudrate = None
        self._hardware_version = None
        self._software_version = None

        self._mode_details: List[ModeDetails] = []
        self._combi_modes: List[CombiModes] = []

        # selected combi or single mode
        self._selected_read_mode: CombiModes | None = None
        self._data_update_interval = 50

        try:
            self._populate_model_details()
        except Exception as e:
            if self._hat.debug:
                print("Failed to parse active sensor details", file=sys.stderr)
                traceback.print_exception(e, file=sys.stderr)
            return

        # Deselect any previous read mode
        self.hat.serial.write(f"port {self.port}; select\r")

        # Deconfigure any previous combi mode
        for c in self._combi_modes:
            self.hat.serial.write(f"port {self.port}; combi {c.number}\r")

        if self._hat.debug:
            print(
                f"  Baudrate={self._baudrate}, HW ver={self._hardware_version}, SW ver={self._software_version}"
            )
            mode_list = [x.name for x in self._mode_details]
            print(f"  Num modes={len(self._mode_details)} {mode_list}")
            if self._combi_modes:
                print(f"  Combi modes:")
                for c in self._combi_modes:
                    print(f"    {c}")

    @property
    def baudrate(self) -> int | None:
        """Sensor communication speed"""
        return self._baudrate

    @property
    def hardware_version(self) -> int | None:
        """Sensor hardware version"""
        return self._hardware_version

    @property
    def software_version(self) -> int | None:
        """Sensor software verion"""
        return self._software_version

    @property
    def data_update_interval(self) -> int:
        """Data update interval in ms when a combi or single read mode is selected"""
        return self._data_update_interval

    @data_update_interval.setter
    def data_update_interval(self, interval: int) -> None:
        if not isinstance(interval, int) or interval < 1:
            raise ValueError("Interval value must be a positive integer greater than 1")

        self._data_update_interval = interval

    def select_read_mode(self, mode: CombiModes | int) -> None:
        """Select a continuos read for combimode or single mode

        :param modev: A CombiMode or a single mode number
        :return: True if mode has been changed or False if mode was already selected
        """
        self.ensure_connected()
        if self._selected_read_mode == mode:
            return False

        # Deselect any previous read mode
        self.hat.serial.write(f"port {self.port}; select\r")

        # Deconfigure the previous combi mode
        if isinstance(self._selected_read_mode, CombiModes):
            self.hat.serial.write(
                f"port {self.port} ; combi {self._selected_read_mode.number}\r"
            )
            self._selected_read_mode = None

        if isinstance(mode, CombiModes):
            # Configure and select the combi mode
            modestr = " ".join([f"{m} 0" for m in mode.modes])
            self.hat.serial.write(
                f"port {self.port} ; combi {mode.number} {modestr} ; select {mode.number} ; selrate {self._data_update_interval}\r"
            )
            self._selected_read_mode = mode
        elif isinstance(mode, int):
            self.hat.serial.write(
                f"port {self.port} ; select {mode} ; selrate {self._data_update_interval}\r"
            )
            self._selected_read_mode = mode
        else:
            raise ValueError("Invalid mode argument")

        return True

    def _populate_model_details(self):
        """
        Active sensor details data example

        type 4B
        nmodes =5
        nview  =3
        baud   =115200
        hwver  =00000004
        swver  =10000000
        M0 POWER SI = PCT
            format count=1 type=0 chars=4 dp=0
            RAW: 00000000 00000064    PCT: 00000000 00000064    SI: 00000000 00000064
        M1 SPEED SI = PCT
            format count=1 type=0 chars=4 dp=0
            RAW: 00000000 00000064    PCT: 00000000 00000064    SI: 00000000 00000064
        M2 POS SI = DEG
            format count=1 type=2 chars=11 dp=0
            RAW: 00000000 00000168    PCT: 00000000 00000064    SI: 00000000 00000168
        M3 APOS SI = DEG
            format count=1 type=1 chars=3 dp=0
            RAW: 00000000 000000B3    PCT: 00000000 000000C8    SI: 00000000 000000B3
        M4 CALIB SI = CAL
            format count=2 type=1 chars=5 dp=0
            RAW: 00000000 00000E10    PCT: 00000000 00000064    SI: 00000000 00000E10
        M5 STATS SI = MIN
            format count=14 type=1 chars=5 dp=0
            RAW: 00000000 0000FFFF    PCT: 00000000 00000064    SI: 00000000 0000FFFF
        C0: M1+M2+M3
            speed PID: 00000BB8 00000064 00002328 00000438
        position PID: 00002EE0 000003E8 00013880 00000000
        P0: established serial communication with active ID 4B

        We will have a predictable way to read all this.
        expect: type 4B
        """
        line = self._hat.readline()
        if not line.startswith(_DETAILS_TYPE_ACTIVE):
            return

        # expect: nmodes =5
        line = self._hat.readline()
        num_modes = int(line[len(_DETAILS_N_MODES) :]) + 1
        # expect: nview  =3
        line = self._hat.readline()
        # expect: baud   =115200
        line = self._hat.readline()
        self._baudrate = int(line[len(_DETAILS_BAUD) :])
        # expect: hwver  =00000004
        line = self._hat.readline()
        self._hardware_version = int(line[len(_DETAILS_HARDWARE_VERSION) :], 16)
        # expect: swver  =10000000
        line = self._hat.readline()
        self._software_version = int(line[len(_DETAILS_SOFTWARE_VERSION) :], 16)

        mode_data_types = ["byte", "short", "int", "float"]
        for i in range(num_modes):
            mode_number = i
            # expect:   M0 POWER SI = PCT
            # or:  M5 COL O SI = IDX
            # Mi mode_name SI = unit
            line = self._hat.readline()
            # 5 is the number of characters before the name
            unit_pos = line.find(_DETAILS_UNIT)
            mode_name = line[5:unit_pos].strip()
            mode_unit = line[unit_pos + len(_DETAILS_UNIT) :].strip()
            # expect: format count=1 type=0 chars=4 dp=0
            line = self._hat.readline()
            line = line[len(_DETAILS_FORMAT_COUNT) :]
            for data in line.strip().split(" "):
                d, v = data.split("=")
                if d == "count":
                    num_of_data = v
                elif d == "type":
                    v = int(v)
                    if v < len(mode_data_types):
                        data_type = mode_data_types[v]
                    else:
                        data_type = ""
                elif d == "chars":
                    number_of_chars = int(v)
                elif d == "dp":
                    decimal_precision = int(v)

            # expect: RAW: 00000000 00000064    PCT: 00000000 00000064    SI: 00000000 00000064
            line = self._hat.readline()
            raw_min_max = MinMaxValue(
                ModeTypeValue.RAW, min=int(line[9:17], 16), max=int(line[18:26], 16)
            )
            percent_min_max = MinMaxValue(
                ModeTypeValue.PERCENT,
                min=int(line[35:43], 16),
                max=int(line[44:54], 16),
            )
            signal_min_max = MinMaxValue(
                ModeTypeValue.SIGNAL, min=int(line[60:68], 16), max=int(line[69:77], 16)
            )

            mode_details = ModeDetails(
                mode_number,
                mode_name,
                mode_unit,
                data_type,
                number_of_chars,
                num_of_data,
                decimal_precision,
                min_max_values={
                    raw_min_max.value_type: raw_min_max,
                    percent_min_max.value_type: percent_min_max,
                    signal_min_max.value_type: signal_min_max,
                },
            )
            self._mode_details.append(mode_details)

        # Now we should or not expect: C0: M1+M2+M3
        has_combi = False
        combi_num = 0
        while True:
            line = self._hat.readline()
            has_combi = line.strip().startswith(f"C{combi_num}: ")
            if has_combi:
                line = line.split(":")[1].strip()
                data = line.split("+")
                modes = [int(x[1:]) for x in data]
                combi = CombiModes(combi_num, modes)
                self._combi_modes.append(combi)
                combi_num += 1
            else:
                break

        # If no combi, then it's speed PID
        # Skip speed PID

        # Read and skip also position PID
        line = self._hat.readline()

    def on_combi_value_update(self, combi_num: int, values: List[str]):
        """BuildHat call this function when there is a device value update from a combo mode"""
        pass

    def on_single_value_update(self, mode: int, value: str):
        """BuildHat call this function when there is a device value update from a single mode"""
        pass

    def _decode_combi_update(
        self, combi_num: int, values: List[str]
    ) -> Dict[ModeDetails, str] | None:
        """Decode a combi value update and return a dictionary with a ModeDetails and value pairs"""
        combi = self._selected_read_mode
        if isinstance(combi, CombiModes):
            if combi_num == combi.number and len(values) == len(combi.modes):
                result = {}
                for i in range(len(values)):
                    mode_num = combi.modes[i]
                    mode = self._mode_details[mode_num]
                    result[mode] = values[i]

                return result
        return None
