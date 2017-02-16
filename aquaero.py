import ctypes, hid
from report import createReport

def dict_match(value, criteria):
  return all(value[k] == v for k, v in criteria.items())

def find_devices(criteria, group = None):
  found = (info for info in hid.enumerate() if dict_match(info, criteria))
  if group is None: return found
  grouped = {}
  for info in found:
    key = info[group]
    if key in grouped:
      grouped[key].append(info)
    else:
      grouped[key] = [info]
  return grouped

class Aquaero(object):
  def __init__(self):
    self._isOpen = False
    self._device = hid.device()

  def open(self, serial_number):
    if self._isOpen:
      self._device.close()
    criteria = {
      'vendor_id': 0x0c70,
      'product_id': 0xf001,
      'serial_number': serial_number
    }
    dev = find_devices(criteria, 'interface_number')
    if len(dev) == 0:
      raise ValueError('unable to find that serial number')
    if 2 not in dev:
      raise IOError('unable to open device interface')
    self._device.open_path(dev[2][0]['path'])
    self._isOpen = True

  def setOutput(self, output, value):
    if not self._isOpen:
      raise IOError('device is not open')
    if len(output) > 5 or output[:3] != 'fan':
      raise ValueError('only fans currently are supported')
    fanNumber = int(output[3:])
    if not (fanNumber >= 1 and fanNumber <= 12):
      raise ValueError('fan number must be in the range 1 to 12')
    if not ((value >= 0 and value <= 100) or value == -1):
      raise ValueError('value must be in the range 0 to 100')
    outValue = int(value * 100)
    outBytes = [0xff, 0xff] if value == -1 else [outValue >> 8, outValue & 0xff]
    self._device.write([0x06, 0x00, 0x63 + fanNumber, 0x00, 0x00] + outBytes)

  def resetOutput(self, output):
    self.setOutput(output, -1)

  def read(self):
    if not self._isOpen:
      raise IOError('device is not open')
    data = self._device.read(1038)
    report = createReport(bytes(data))
    report._data = data
    return report

  def close(self):
    if self._isOpen:
      self._device.close()
      self._isOpen = False
