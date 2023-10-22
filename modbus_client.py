#!/usr/bin/env python3

import argparse
import sys
import time

from pymodbus.client import ModbusSerialClient as ModbusClient


DEFAULT_METHOD = "rtu"
DEFAULT_BAUD = 9600

BYTESIZE_CHOICES = [7, 8]
DEFAULT_BYTESIZE = 8
DEFAULT_STOPBITS = 1

PARITY_CHOICES = ["N", "E", "O"]
DEFAULT_PARITY = "N"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='modbus-client')
    parser.add_argument("--device", required=True, type=str)
    parser.add_argument("--baudrate", help=f"baud rate", default=DEFAULT_BAUD, type=int, required=True)
    parser.add_argument("--bytesize", help=f"bytes size (default: {DEFAULT_BYTESIZE})", default=DEFAULT_BYTESIZE, type=int, choices=BYTESIZE_CHOICES)
    parser.add_argument("--stopbits", help=f"stop bits (default: {DEFAULT_STOPBITS})", default=DEFAULT_STOPBITS, type=int)
    parser.add_argument("--parity", help=f"parity (default: {DEFAULT_PARITY})", default=DEFAULT_PARITY, choices=PARITY_CHOICES)
    parser.add_argument("--unit", help=f"slave unit address", required=True, type=int)
    parser.add_argument("--read-input", metavar="ADDRESS", help=f"read input register", type=int)
    parser.add_argument("--read-holding", metavar="ADDRESS", help=f"read holding register", type=int)
    parser.add_argument("--write-holding", metavar="X", nargs=2, help=f"write holding register", type=int)
    args = parser.parse_args()

    client = ModbusClient(port=args.device, baudrate=args.baudrate, bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits, timeout=1, retries=1)
    client.connect()

    if not client.is_socket_open():
        print("failed")
        sys.exit(1)

    try:
        if args.read_input is not None:
            assert client.is_socket_open()
            r = client.read_input_registers(address=args.read_input, count=1, slave=args.unit)
            print(r)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(r.registers[0])

        if args.read_holding is not None:
            assert client.is_socket_open()
            r = client.read_holding_registers(address=args.read_holding, count=1, slave=args.unit)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(r.registers[0])

        if args.write_holding is not None:
            assert client.is_socket_open()
            r = client.write_register(address=args.write_holding[0], value=args.write_holding[1], count=1, slave=args.unit)
            if r.isError():
                print(r)
                sys.exit(1)
            else:
                print(r.registers)

    finally:
        client.close()
