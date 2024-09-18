# SPDX-FileCopyrightText: Copyright (c) 2024 Dario Cammi
#
# SPDX-License-Identifier: MIT


def validate_port(port: int) -> None:
    if not isinstance(port, int):
        ValueError("Port must be an integer number")
    if port < 0 or port > 3:
        raise ValueError("Port number out of range. It must be 0,1,2 or 3")
