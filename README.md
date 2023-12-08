Ferroli Omnia heat pump modbus interface
========================================

Ferroli Omnia is a heat pump range produced by Midea. It is a white label
product, also sold under other names, including:

* Ferroli Omnia 3.2 monobloc
* Midea M thermal Modo
* Airwell Wellea Monobloc A
* Lamborghini Idola M 3.2
* Artel Linea Monobloc

The heat pump comes as a monobloc with an outdoor hydrolic unit and an indoor
controller unit. The controller unit communicates with the hydrolic unit via
a wire and optionally uses Wifi to connect with the cloud and the (not so
great)
[Android](https://play.google.com/store/apps/details?id=com.cacapp.omnia)
or [Apple](https://apps.apple.com/nl/app/omnia-smart/id1532349739) app.

The controller also supports [Modbus](https://en.wikipedia.org/wiki/Modbus),
a serial protocol widely used for building management. This page shows some
experiments with this interface.


Why?
----

Modbus can be used to control the device. Turn it on or off and set the
desired water temperature. Also read sensor values, such as fan speed.

* It allows for fine grained control (contrary to e.g. thermostat on/off).
* What is local stays local, no cloud involved.
* Integrates with domotica, such as [Home Assistant](https://www.home-assistant.io/).

The alternative is to use the cloud or wifi, as implemented by, for example,
the custom integration [Midea AC LAN](https://github.com/georgezhao2010/midea_ac_lan)
for Home Assistant.


Connecting the remote controller
--------------------------------

Modbus requires three wires, usually labeled A+, B- and Gnd. Connect the wires
to H2, H1 and E respectively. These terminals can be found in the
controller by removing it from the mounting plate.

Connect as follows:

* **H2** -> **A+**
* **H1** -> **B-**
* **E** -> **Gnd**

**Note: according to the Ferroli manual, the H1 and H2 should be reversed. That
didn't work for me!**

When setting up a serial connection (rs485), you will need to configure the
correct parameters. The factory defaults are:

* baudrate: 9600
* byte size: 8
* parity: none
* stop bits: 1

and the modbus parameters are:

* modbus method: RTU
* modbus slave: 1


These settings cannot be changed.


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

If you want to play with more values, check out the modbus register
addresses listed in the controller manual (see
[Documentation](#documentation)). Have fun!


Integrating Home Assistant using the Modbus integration
-------------------------------------------------------

Home assistant supports [modbus
entities](https://www.home-assistant.io/integrations/modbus/). There are two
options. The simplest is to connecting it directly to the device running Home
Assistant via USB. Alternatively, use an another device like a Raspberry Pi
and expose modbus to Home Assistant via RTU over TCP using
[ser2net](https://linux.die.net/man/8/ser2net).


Integrating Home Assistant via Esphome
--------------------------------------

See the `modbus/omnia.yaml` file for Omnia specific configuration, or
`esphome.yaml` for a full setup.


Operating the Omnia heatpump
----------------------------

Some observations:

- eco mode seems to disable modulation and ignore water temperature setpoint
  (this may be specific to my setup);

- most of the settings can't be changed while the heat pump is active, or it
  will turn itself off;

- input power limitation: 0 = no limit (per user manual), the higher the
  value, the lower the maximum power usage?;


Glossary
--------

* AHS: Auxiliary Heating System (external heater)
* DHW: Domestic Hot Water
* IBH: Interal Backup Heating (electric heater)
* PMV: pulse modulating valve
* T1: system water outlet temperature (behind auxiliary heater)
* T1S: desired water outlet temperature
* T1S2: desired water outlet temperature for zone 2
* T2: refrigerant liquid side temperature sensor
* T2B: refrigerant gas side temperature sensor
* T3: condenser temperature sensor
* T4: outdoor ambient temperature sensor
* T5: water tank temperature sensor
* Ta: room temperature
* TBH: electric water tank heater


Documentation
-------------

* Ferroli Wired Remote Controller manual ([PDF](https://www.ferroli.com/media/3QE47730_00_MIU_Comando%20remoto%20cablato_EN_12x12.pdf))
