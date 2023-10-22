Ferroli Omnia heat pump modbus interface
========================================

Ferroli Omnia is a heat pump range produced by Midea. It is a white label
product, also sold as:

* Ferroli Omnia 3.2 monobloc

* Midea M thermal Modo

* Airwell Wellea Monobloc A

* Lamborghini Idola M 3.2

* Artel Linea Monobloc

The heat pump comes as a monobloc with an outdoor hydrolic unit and an indoor
controller unit. The controller unit communicates with the hydrolic unit via
a wire and optionally uses Wifi to connect with the cloud and the app.

The controller also supports [Modbus](https://en.wikipedia.org/wiki/Modbus),
a serial protocol widely used for building management. This page shows some
experiments with this interface.


Why?
----

Modbus can be used to control the device. Turn it on or off and set the
desired water temperature. Also read sensor values, such as fan speed.

* It allows for fine grained control (contrary to e.g. thermostat on/off).

* What is local stays local, no cloud involved.

* Integrates with domotica, e.g. Home Assistant.


Connecting the remote controller
--------------------------------

Modbus requires three wires, usually labeled A+, B- and Gnd. Connect the wires
to H2, H1 and E respectively. These terminals can be found in the
controller by removing the back plate.

**Note: according to the Ferroli manual the H1 and H2 should be reversed. That
didn't work for me!**


Modbus via USB
--------------

To connect via USB, get a USB to RS485 adapter. Connect the three modbus wires
from the controller to the adapter, A+ to A+, B- to B- and Gnd to Gnd.

Figure out the name of the USB port and make sure you have write
permissions. On Ubuntu the device is typically called `/dev/ttyUSB0` or
similar.

Use `omnia.py` to control the heat pump or read info from the device.

```sh
./omnia.py --help
./omnia.py --device=/dev/ttyUSB0 --read-info
```

Have fun!


Integrating Home Assistant using the Modbus integration
-------------------------------------------------------

Home assistant supports [modbus
entities](https://www.home-assistant.io/integrations/modbus/). There are two
options. The simplest is to connecting it directly to the device running Home
Assistant via USB. Alternatively, use an another device like a Raspberry Pi
and expose modbus to Home Assistant via RTU over TCP using
[ser2net](https://linux.die.net/man/8/ser2net).

In both cases you need serial connection parameters to connect. The factory
defaults are:

* modbus method: RTU
* modbus slave: 1
* baud: 9600
* byte size: 8
* stop bits: 1
* parity: N


Documentation
-------------

* [Ferroli Wired Remote Controller](https://www.ferroli.com/media/3QE47730_00_MIU_Comando%20remoto%20cablato_EN_12x12.pdf)
