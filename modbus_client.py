#!/usr/bin/env python3

import argparse
import collections
import os
import sys
import time
from typing import Callable

from pymodbus.client import ModbusSerialClient as ModbusClient


def parse_int(s: str) -> int:
    if s.startswith('0x'):
        return int(s, 16)
    else:
        return int(s)


DEFAULT_METHOD = "rtu"
DEFAULT_BAUD = 9600

BYTESIZE_CHOICES = [7, 8]
DEFAULT_BYTESIZE = 8

STOPBITS_CHOICES = [1, 2]
DEFAULT_STOPBITS = 1

PARITY_CHOICES = ["N", "E", "O"]
DEFAULT_PARITY = "N"
DEFAULT_SLAVE = 1

RegisterType = collections.namedtuple("RegisterType", ["name", "size", "parse"])
REGISTER_TYPE_U_WORD = RegisterType("U_WORD", 1, lambda v: v[0])
REGISTER_TYPE_S_WORD = RegisterType("S_WORD", 1, lambda v: v[0])
REGISTER_TYPE_U_DWORD = RegisterType("U_DWORD", 2, lambda v: (v[0] << 16) | v[1])
REGISTER_TYPE_S_DWORD = RegisterType("S_DWORD", 2, lambda v: (v[0] << 16) | v[1])

REGISTER_TYPES = [
    REGISTER_TYPE_U_WORD,
    REGISTER_TYPE_S_WORD,
    REGISTER_TYPE_U_DWORD,
    REGISTER_TYPE_S_DWORD,
]


def add_modbus_arguments(parser, default_baud=DEFAULT_BAUD, default_bytesize=DEFAULT_BYTESIZE, default_stopbits=DEFAULT_STOPBITS, default_parity=DEFAULT_PARITY, default_slave=DEFAULT_SLAVE):
    modbus_args = parser.add_argument_group("modbus and serial settings")
    modbus_args.add_argument("--device", metavar="DEV", required=True, type=str, help="connect to device")
    modbus_args.add_argument("--baudrate", help=f"baud rate (default: {default_baud})", default=default_baud, type=int)
    modbus_args.add_argument("--bytesize", help=f"bytes size (default: {default_bytesize})", default=default_bytesize, type=int, choices=BYTESIZE_CHOICES)
    modbus_args.add_argument("--stopbits", help=f"stop bits (default: {default_stopbits})", default=default_stopbits, type=int, choices=STOPBITS_CHOICES)
    modbus_args.add_argument("--parity", help=f"parity (default: {default_parity})", default=default_parity, choices=PARITY_CHOICES)
    modbus_args.add_argument("--slave", metavar="{0..255}", help=f"slave unit address (default: {default_slave}; use 0 for broadcast)", default=default_slave, type=int)

    modbus_actions = parser.add_argument_group("modbus actions")
    modbus_actions.add_argument("--read-input", metavar="A", help=f"read input register at address A", type=parse_int)
    modbus_actions.add_argument("--read-holding", metavar="A", help=f"read holding register at address A", type=parse_int)
    modbus_actions.add_argument("--write-holding", metavar=("A", "V"), nargs=2, help=f"write value V to holding register A", type=parse_int)
    modbus_actions.add_argument("--register-type", metavar="TYPE", help=f"register type", choices=[r.name for r in REGISTER_TYPES], default=REGISTER_TYPE_S_WORD)


def run(appname, add_arguments: Callable = None, run_actions: Callable = None):
    parser = argparse.ArgumentParser(prog=appname)
    add_modbus_arguments(parser)

    if add_arguments is not None:
        add_arguments(parser)

    args = parser.parse_args()
    register_type = [r for r in REGISTER_TYPES if r.name == args.register_type][0]

    client = ModbusClient(port=args.device, baudrate=args.baudrate, bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits, timeout=1, retries=1)
    client.connect()

    if not client.is_socket_open():
        print("failed")
        sys.exit(1)

    try:
        if args.read_input is not None:
            assert client.is_socket_open()
            r = client.read_input_registers(address=args.read_input, count=register_type.size, slave=args.slave)
            print(r)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(register_type.parse(r.registers))

        if args.read_holding is not None:
            assert client.is_socket_open()
            r = client.read_holding_registers(address=args.read_holding, count=register_type.size, slave=args.slave)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(register_type.parse(r.registers))

        if args.write_holding is not None:
            assert client.is_socket_open()
            r = client.write_register(address=args.write_holding[0], value=args.write_holding[1], count=register_type.size, slave=args.slave)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(r.registers)

        if run_actions is not None:
            run_actions(client, args)

    finally:
        client.close()


if __name__ == "__main__":
    run(os.path.basename(__file__))
