pyaquaero
=========

A simple python interface to access and control an aquaero.

Install
-------

Depends on the [hid](https://github.com/trezor/cython-hidapi) module.

Clone this repo, import the `aquaero` module.

Compatibility
-------------

Only known to support the Aquaero 6 XT. May support other devices. Use at your own risk.

Usage
-----

```py
>>> from aquaero import Aquaero
>>> device = Aquaero()
>>> device.open(serial_number) # a string, in the form #####-#####
>>> report = device.read()
>>> report.temperatures[:4]
[2714, 3085, 32767, 32767] # 32767 denotes a null value
>>> report.fans[0]
<ReportFanData rpm: 1534, power: 7886, voltage: 956, current: 234, performance: 223, torque: 138>
>>> device.setOutput('fan1', 85.0) # set the first fan to 85%
>>> device.resetOutput('fan1') # reset the fan to its default behavior
```

API
---

### Aquaero()

Create a new Aquaero device.

### Aquaero#open(serial_number)

Open the Aquaero device for the given serial number.

### Aquaero#read()

Read a Report from the device.

### Aquaero#setOutput(output, value)

Set the given output to the given percent value.

### Aquaero#resetOutput(output)

Reset the given output to its default behavior.

### Aquaero#close()

Close the device.

License
-------

The MIT License.
