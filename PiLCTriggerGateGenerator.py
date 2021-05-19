#!/usr/bin/env python3
from tango import AttrWriteType, DevState, DispLevel, DeviceProxy, Database
from tango.server import Device, attribute, command, device_property
from enum import IntEnum


class Mode(IntEnum):
    freerunning = 0
    triggered_laser = 1
    triggered_laser_ccd = 2


class PiLCTriggerGateGenerator(Device):
    '''PiLCTriggerGateGenerator

    Provides high-level access to the PiLC Tango interface

    '''

    PiLCFQDN = device_property(dtype=str, default_value='domain/family/member')

    exposure = attribute(
        dtype=int,
        format="%8d",
        label="Exposure",
        unit="ms",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.OPERATOR,
        doc="Exposure time in full 10ms steps",
        memorized=True,
    )

    mode = attribute(
        dtype=Mode,
        label="Mode",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.OPERATOR,
        memorized=True,
        doc="""
1 - free running
2 - triggered laser
3 - triggered laser & ccd
"""
    )

    def init_device(self):
        Device.init_device(self)
        try: 
            self.pilc = DeviceProxy(self.PiLCFQDN)
            self.info_stream('Connected to PiLC: {:s}'.format(self.PiLCFQDN))
        except:
            self.error_stream('Could not connect to PiLC: {:s}'.format(self.PiLCFQDN))
            return
            self.set_state(DevState.OFF)
        
        self.set_state(DevState.ON)
        self.db = Database()
        try:
            attr = self.db.get_device_attribute_property(self.get_name(), ["exposure"])
            self._exposure = int(attr["exposure"]["__value"][0])
        except Exception:
            self._exposure = -1
        try:
            attr = self.db.get_device_attribute_property(self.get_name(), ["mode"])
            self._mode = int(attr["mode"]["__value"][0])
        except Exception:
            self._mode = 0

    def always_executed_hook(self):
        if self.pilc.ReadFPGA(0x06) > 0:
            self.set_state(DevState.MOVING)
        else:
            self.set_state(DevState.ON)

    # attribute read/write methods
    def read_exposure(self):
        return self._exposure

    def write_exposure(self, value):
        self._exposure = int(round(value/10, 0)*10)

    def read_mode(self):
        return self._mode

    def write_mode(self, value):
        self._mode = value

    # commands
    @command()
    def prepare(self):
        if self._exposure >= 40:
            shutter_gate_width = (self._exposure-8)
        elif self._exposure >= 30:
            shutter_gate_width = (self._exposure-7)
        elif self._exposure >= 20:
            shutter_gate_width = (self._exposure-5)
        else:
            shutter_gate_width = self._exposure

        shutter_gate_delay = 0
        keithley_gate_width = self._exposure
        keithley_gate_delay = 8
        quantity = 1

        self.debug_stream('Shutter gate width set to {:d} ms'.format(shutter_gate_width))
        self.debug_stream('Shutter gate delay set to {:d} ms'.format(shutter_gate_delay))
        self.debug_stream('Keithley gate width set to {:d} ms'.format(keithley_gate_width))
        self.debug_stream('Keithley gate delay set to {:d} ms'.format(keithley_gate_delay))
        self.debug_stream('Quantity set to {:d}'.format(quantity))

        # define gate width in micorseconds
        self.pilc.WriteFPGA([0x03, int(shutter_gate_width*1e3)])
        # define gate delay in microseconds
        self.pilc.WriteFPGA([0x07, int(shutter_gate_delay*1e3)])

        # define keithley gate width in micorseconds
        self.pilc.WriteFPGA([0x09, int(keithley_gate_width*1e3)])
        # define keithley gate delay in microseconds
        self.pilc.WriteFPGA([0x0B, int(keithley_gate_delay*1e3)])

        # define gate quantity
        self.pilc.WriteFPGA([0x05, int(quantity)])

    @command()
    def stop(self):
        self.debug_stream('Stop')
        self.pilc.WriteFPGA([0x01, 0])

    @command()
    def start(self):
        self.debug_stream('Start in {:s} mode'.format(Mode(self._mode).name))
        self.pilc.WriteFPGA([0x01, self._mode+1])

    @command()
    def acquire(self):
        self.debug_stream('Acquire')
        self.stop()
        self.prepare()
        self.start()
    

# start the server
if __name__ == "__main__":
    PiLCTriggerGateGenerator.run_server()
