from .minmaxvalue import MinMaxValue
from .modetypevalue import ModeTypeValue

try:
    from typing import Dict
except:
    pass


class ModeDetails:
    def __init__(
        self,
        number: int,
        name: str,
        unit: str,
        data_type: str,
        num_of_chars_to_display: int,
        num_of_data: int,
        decimal_precision: int,
        min_max_values: Dict[ModeTypeValue, MinMaxValue],
    ):
        self._number = number
        self._name = name
        self._unit = unit
        self._data_type = data_type
        self._num_of_chars_to_display = num_of_chars_to_display
        self._num_of_data = num_of_data
        self._decimal_precision = decimal_precision
        self._min_max_values = min_max_values

    @property
    def number(self) -> int:
        """Mode number"""
        return self._number

    @property
    def name(self) -> str:
        """Mode name"""
        return self._name

    @property
    def unit(self) -> str:
        """Mode value unit"""
        return self._unit

    @property
    def data_type(self) -> str:
        """Mode value type: byte, short, int, float"""
        return self._data_type

    @property
    def num_of_chars_to_display(self) -> int:
        """Mode number of chars to display for value"""
        return self._num_of_chars_to_display

    @property
    def num_of_data(self) -> int:
        """Mode number of data values"""
        return self._num_of_data

    @property
    def decimal_precision(self) -> int:
        """Mode value decimal precision. Only for data_type float, 0 otherwise"""
        return self._decimal_precision

    @property
    def min_max_values(self) -> Dict[ModeTypeValue, MinMaxValue]:
        """Mode minimum and maximum values for raw, percentage and signal value"""
        return self._min_max_values

    def __str__(self) -> str:
        result = f"Mode {self._number}: {self._name}\n"
        result += f"  Unit: {self._unit}, Data type: {self._data_type}, Num of values: {self._num_of_data}\n"
        for x in self._min_max_values:
            result += f"  Min-Max: {self._min_max_values[x]}\n"
        return result
