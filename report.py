import ctypes, numbers

# derived from
# https://github.com/aquacomputer/plugin_sdk/blob/1b8b154/DeviceSdk/aquaero_5_6_aquaduct_mk_4_5/structure_version_1200/data_layout_1200.h
# the aquaero 6 XT does not follow the spec perfectly

def normalizeValue(obj):
  if isinstance(obj, ctypes.Array):
    return list(obj)
  return obj

def normalize(obj):
  return {k[0]: normalizeValue(getattr(obj, k[0])) for k in obj._fields_}

def formatValue(value):
  if value is None: return ''
  if isinstance(value, str): return ': ' + value
  return ': ' + repr(value)

def filterFeatures(features, getter = None):
  if isinstance(getter, list):
    getter = lambda i: getter[i]
  return filter(getter, features)

def formatFeatures(features):
  return ', '.join(':' + name for name in features)

def formatDict(obj, valueFunc = formatValue):
  return ', '.join(str(key) + valueFunc(value) for key, value in obj.items())

def simpleFormat(obj):
  if isinstance(obj, ctypes.Structure): return ''
  if isinstance(obj, list): return ' ({:d})'.format(len(obj))
  return formatValue(obj)

deviceCapabilities = ['display', 'keys', 'touch', 'remote']

class ReportDeviceCapabilities(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('bits', ctypes.c_uint16)]

  def __repr__(self):
    l = formatFeatures(self.listCapabilities())
    return '<ReportDeviceCapabilities' + (' ' if len(l) else '') + l + '>'

  def listCapabilities(self):
    return list(filterFeatures(deviceCapabilities, lambda f: getattr(self, 'has' + f[0].upper() + f[1:])()))

  def hasDisplay(self):
    return bool(self.bits & 1)

  def hasKeys(self):
    return bool(self.bits & 2)

  def hasTouch(self):
    return bool(self.bits & 4)

  def hasRemote(self):
    return bool(self.bits & 8)

deviceTypes = {
  0: 'Aquaero 5 LT',
  1: 'Aquaero 5 PRO',
  2: 'Aquaero 5 XT',
  3: 'Aquaduct MK4 361',
  4: 'Aquaduct MK4 360',
  5: 'Aquaduct MK4 720',
  6: 'Aquaduct MK5 360',
  7: 'Aquaduct MK5 720'
}

class ReportDeviceInfo(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('serial', ctypes.c_uint16 * 2),
              ('firmware', ctypes.c_uint16),
              ('bootloader', ctypes.c_uint16),
              ('hardware', ctypes.c_uint16),
              ('uptime', ctypes.c_uint32),
              ('uptimeTotal', ctypes.c_uint32),
              ('status', ctypes.c_uint8), # enum?
              ('lockControl', ctypes.c_uint16),
              ('type', ctypes.c_uint8),
              ('capabilities', ReportDeviceCapabilities)]

  def __repr__(self):
    rep = normalize(self)
    rep['serial'] = '\'{:05d}-{:05d}\''.format(*rep['serial'])
    rep['type'] = '{:d} ({:s})'.format(self.type, deviceTypes.get(self.type, 'unknown'))
    rep['capabilities'] = None
    return '<ReportDeviceInfo ' + formatDict(rep) + '>'

aquabusStatusFields = [
  'aquastream1',
  'aquastream2',
  'poweradjust1',
  'poweradjust2',
  'poweradjust3',
  'poweradjust4',
  'poweradjust5',
  'poweradjust6',
  'poweradjust7',
  'poweradjust8',
  'mps1',
  'mps2',
  'mps3',
  'mps4',
  'rtc',
  'aquaero5slave',
  'farbwerk1',
  'farbwerk2'
]

class ReportAquabusStatus(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('bits', ctypes.c_uint32)]

  def __getattribute__(self, name):
    try:
      index = aquabusStatusFields.index(name)
    except ValueError:
      return super(ReportAquabusStatus, self).__getattribute__(name)
    return int(bool(self.bits & (1 << index)))

  def __repr__(self):
    active = self.listActive()
    if len(active):
      return '<ReportAquabusStatus ' + formatFeatures(active) + '>'
    else:
      return '<ReportAquabusStatus>'

  def listActive(self):
    return list(filterFeatures(aquabusStatusFields, lambda f: getattr(self, f)))

class ReportPowerConsumption(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('flow', ctypes.c_int16),
              ('sensor1', ctypes.c_int16),
              ('sensor2', ctypes.c_int16),
              ('deltaT', ctypes.c_int16),
              ('power', ctypes.c_int16),
              ('rth', ctypes.c_int16)]

  def __repr__(self):
    return '<ReportPowerConsumption ' + formatDict(normalize(self)) + '>'

class ReportFanData(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('rpm', ctypes.c_int16),
              ('power', ctypes.c_int16),
              ('voltage', ctypes.c_int16),
              ('current', ctypes.c_int16),
              ('performance', ctypes.c_int16),
              ('torque', ctypes.c_int16)]

  def __repr__(self):
    return '<ReportFanData ' + formatDict(normalize(self)) + '>'

class ReportAquastreamStatus(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('data', ctypes.c_uint8)]

  def __repr__(self):
    rep = {
      'available': self.isAvailable(),
      'alarmActive': self.isAlarmActive()
    }
    return '<ReportAquastreamStatus ' + formatDict(rep) + '>'

  def isAvailable(self):
    return bool(self.data & 1)

  def isAlarmActive(self):
    return bool(self.data & 2)

class ReportPumpData(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('status', ReportAquastreamStatus),
              ('mode', ctypes.c_uint8), # enum
              ('rpm', ctypes.c_int16),
              ('voltage', ctypes.c_int16),
              ('current', ctypes.c_int16)]

  def __repr__(self):
    rep = normalize(self)
    rep['status'] = None
    return '<ReportPumpData ' + formatDict(rep) + '>'

class ReportControllers(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('twoPoint', ctypes.c_int16 * 16),
              ('constant', ctypes.c_int16 * 32),
              ('colorLED', ctypes.c_int16 * 12),
              ('setPoint', ctypes.c_int16 * 8),
              ('curve', ctypes.c_int16 * 4)]

  def __repr__(self):
    return '<ReportControllers ' + formatDict(normalize(self)) + '>'

class Report(ctypes.BigEndianStructure):
  _pack_ = 1
  _fields_ = [('id', ctypes.c_uint8),
              ('timestamp', ctypes.c_uint32),
              ('version', ctypes.c_uint16),
              
              ('deviceInfo', ReportDeviceInfo),
              ('lastSettingsUpdateTime', ctypes.c_uint32),

              ('lcdstate', ctypes.c_uint8 * 20),
              ('alarmLevel', ctypes.c_uint8), # enum
              ('actualProfile', ctypes.c_uint8),
              ('aquabus', ReportAquabusStatus), # 32bit

              ('adcRaw', ctypes.c_uint16 * 20),
              ('temperatures', ctypes.c_int16 * 64),
              ('rawRpmFlow', ctypes.c_uint32 * 5),
              ('flow', ctypes.c_uint16 * 14),
              ('powerConsumption', ReportPowerConsumption * 4),
              ('level', ctypes.c_int16 * 4),
              ('humidity', ctypes.c_int16 * 4),
              ('conductivity', ctypes.c_int16 * 4),
              ('pressure', ctypes.c_int16 * 4),

              ('tacho', ctypes.c_int16),
              ('fans', ReportFanData * 12), # only 4 implemented
              ('aquastream', ReportPumpData * 8),
              ('outputAvailable', ctypes.c_uint32), # this is supposed to be * 2 per the spec
              ('outputs', ctypes.c_int16 * 64),
              ('controllers', ReportControllers)]

  def __repr__(self):
    return '<Report ' + formatDict(normalize(self), simpleFormat) + '>'

def createReport(data):
  return Report.from_buffer_copy(data)
