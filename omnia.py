#!/usr/bin/env python3

import argparse
from collections import namedtuple
import os
import sys
import time

from pymodbus.client import ModbusSerialClient as ModbusClient

from modbus_client import run


DEFAULT_METHOD = "rtu"
DEFAULT_BAUD = 9600

BYTESIZE_CHOICES = [7, 8]
DEFAULT_BYTESIZE = 8
DEFAULT_STOPBITS = 1

PARITY_CHOICES = ["N", "E", "O"]
DEFAULT_PARITY = "N"
DEFAULT_SLAVE = 1


class Omnia:
    def __init__(self, client, slave):
        self.client = client
        self.slave = slave

    def read_register(self, address: int):
        assert self.client.is_socket_open()
        r = self.client.read_holding_registers(address=address, count=1, slave=self.slave)
        if r.isError():
            print(r)
            sys.exit(1)
        else:
            return r.registers[0]

    def write_register(self, address, value):
        assert self.client.is_socket_open()
        r = self.client.write_register(address=address, value=value, count=1, slave=self.slave)
        print(r)
        if r.isError():
            sys.exit(1)

    def write_register_bit(self, address: int, bit: int, value: bool):
        mask = 0xffff - (1 << bit)
        old_value = self.read_register(address)
        new_value = (old_value & mask) | (int(value) << bit)
        print(f"update: {old_value} -> {new_value}")
        self.write_register(address, new_value)

    def read_info(self):
        for reg in REGISTERS:
            value = self.read_register(reg.address)
            line = f"{reg.desc}: {reg.func(value)}"
            if reg.unit is not None:
                line += f"{reg.unit}"
            print(line)
        print(f"Energy consumption: {self.get_power_consumption()} kWh")
        print(f"Energy output: {self.get_power_output()} kWh")

    def set_mode(self, value: str):
        if value == "auto":
            self.write_register(1, 1)
        elif value == "cool":
            self.write_register(1, 2)
        elif value == "heat":
            self.write_register(1, 3)
        else:
            raise ValueError()

    def get_power_consumption(self):
        v1 = self.read_register(143)
        v2 = self.read_register(144)
        return (v1 << 16) + v2

    def get_power_output(self):
        v1 = self.read_register(145)
        v2 = self.read_register(146)
        return (v1 << 16) + v2

    def set_cool_mode(self):
        self.write_register(1, 2)

    def set_zone1_power(self, status: bool):
        self.write_register_bit(0, 1, status)

    def set_silent(self, status: bool):
        self.write_register_bit(5, 6, status)

    def set_eco_mode(self, status: bool):
        self.write_register_bit(5, 10, status)

    def set_zone1_water_temperature(self, temperature: int):
        self.write_register(11, temperature)

    def set_power_limit(self, value: int):
        if value == "none":
            value = 0

        assert 0 <= value <= 8, "value outside range"
        self.write_register(269, value)


ModbusValue = namedtuple("ModbusValue", ["address", "desc", "unit", "func"])

OPERATING_MODES = {
    0: "off",
    1: "auto",
    2: "cool",
    3: "heat",
}

REGISTERS = [
    ModbusValue(0, "power status zone 1", None, lambda x: bool((x >> 1) & 1)),
    ModbusValue(0, "power status DHW", None, lambda x: bool((x >> 2) & 1)),
    ModbusValue(0, "power status zone 2", None, lambda x: bool((x >> 3) & 1)),
    ModbusValue(0, "power status A/C zone 1", None, lambda x: bool(x & 1)),
    ModbusValue(1, "mode setting", None, lambda x: OPERATING_MODES[x]),
    ModbusValue(5, "silent mode level", None, lambda x: (x >> 7) & 1),
    ModbusValue(5, "silent mode", None, lambda x: bool((x >> 6) & 1)),
    ModbusValue(5, "ECO mode", None, lambda x: bool((x >> 10) & 1)),
    ModbusValue(11, "water temperature zone 1 setting", "C", int),
    ModbusValue(12, "water temperature zone 2 setting", "C", int),
    ModbusValue(100, "Compressor frequency", "Hz", int),
    ModbusValue(101, "actual mode", None, lambda x: OPERATING_MODES[x]),
    ModbusValue(102, "fan speed", "r/min", int),
    ModbusValue(104, "water inlet temperature", "C", int),
    ModbusValue(105, "water outlet temperature", "C", int),
    ModbusValue(106, "condenser temperature", "C", int),
    ModbusValue(107, "outdoor ambient temperature", "C", int),
    ModbusValue(108, "compressor discharge temperature", "C", int),
    ModbusValue(109, "compressor suction temperature", "C", int),
    #ModbusValue(110, "water outlet temperature behind auxiliary heater", "C", int),
    ModbusValue(112, "refrigerant liquid side temperature", "C", int),
    ModbusValue(113, "refrigerant gas side temperature", "C", int),
    ModbusValue(116, "high pressure value", "kPa", int),
    ModbusValue(117, "low pressure value", "kPa", int),
    ModbusValue(118, "operating current", "A", int),
    ModbusValue(119, "operating voltage", "V", int),
    ModbusValue(122, "operating time", "h", int),
    ModbusValue(123, "unit capacity", None, int),
    ModbusValue(124, "error code", None, int),
    ModbusValue(130, "controller software version", None, int),
    ModbusValue(131, "controller hardware version", None, int),
    ModbusValue(133, "DC bus current", "A", int),
    ModbusValue(134, "DC bus voltage", "V", lambda x: x*10),
    ModbusValue(135, "TF module temperature", "C", int),
    ModbusValue(138, "water flow", "m3/h", int),
    ModbusValue(140, "power output", "kW", lambda x: x/100),
    ModbusValue(209, "pump runtime setting", "min", int),
    #ModbusValue(202, "Zone 1 cooling lower limit", "C", lambda x: x & 0xff),
    #ModbusValue(201, "Zone 1 cooling upper limit", "C", lambda x: x & 0xff),
    #ModbusValue(204, "Zone 1 heating lower limit", "C", lambda x: x & 0xff),
    #ModbusValue(203, "Zone 1 heating upper limit", "C", lambda x: x & 0xff),
    #ModbusValue(202, "Zone 2 cooling lower limit", "C", lambda x: x >> 8),
    #ModbusValue(201, "Zone 2 cooling upper limit", "C", lambda x: x >> 8),
    #ModbusValue(204, "Zone 2 heating lower limit", "C", lambda x: x >> 8),
    ModbusValue(210, "enable heating", None, lambda x: bool((x >> 7) & 1)),
    ModbusValue(211, "pipe length >10m", None, lambda x: bool((x >> 11) & 1)),
    ModbusValue(269, "power input limit", None, lambda x: "none" if x==0 else x),
]


def add_arguments(parser):
    omnia_args = parser.add_argument_group("omnia actions")
    omnia_args.add_argument("--read-info", action='store_true', help="read various info from the device")
    omnia_args.add_argument("--power", help='turn power on or off', action=argparse.BooleanOptionalAction)
    omnia_args.add_argument("--silent-mode", help='silent mode on or off', action=argparse.BooleanOptionalAction)
    omnia_args.add_argument("--eco-mode", help='eco mode on or off', action=argparse.BooleanOptionalAction)
    omnia_args.add_argument("--set-water-temp", metavar="TEMP", type=int, help="set desired outlet water temperature")
    omnia_args.add_argument("--mode", choices=["auto", "cool", "heat"])
    omnia_args.add_argument("--set-power-limit", metavar="[0-8]", help="limit input power (use 0 for no limit)", type=int)


def run_actions(client, args):
    omnia = Omnia(client, args.slave)

    if args.power is not None:
        omnia.set_zone1_power(args.power)

    if args.silent_mode is not None:
        omnia.set_silent(args.silent_mode)

    if args.eco_mode is not None:
        omnia.set_eco_mode(args.eco_mode)

    if args.mode is not None:
        omnia.set_mode(args.mode)

    if args.set_water_temp is not None:
        omnia.set_zone1_water_temperature(args.set_water_temp)

    if args.set_power_limit is not None:
        omnia.set_power_limit(args.set_power_limit)

    if args.read_info:
        omnia.read_info()

    if args.read_holding is not None:
        omnia.read_register(args.read_holding)

    if args.write_holding is not None:
        omnia.write_register(args.write_holding[0], value=args.write_holding[1])


if __name__ == "__main__":
    run(os.path.basename(__file__), add_arguments, run_actions)
