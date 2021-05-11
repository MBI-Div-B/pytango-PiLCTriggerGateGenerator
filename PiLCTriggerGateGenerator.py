#!/usr/bin/env python3
from tango import AttrWriteType, DevState, DispLevel, DeviceProxy
from tango.server import Device, attribute, command, device_property

class PiLCTriggerGateGenerator(Device):
    '''PiLCTriggerGateGenerator

    Provides high-level access to the PiLC Tango interface

    '''

    PiLCFQDN = device_property(dtype=str, default='domain/family/member')
    
    # device attributes
    alarm_detected = attribute(
        dtype='bool',
        label='Alarm Detected',
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
        doc='Returns "0" if everything is okay, and "1" if there was an alarm since the reset',
    )
    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.ON)
        try: 
            self.pilc = DeviceProxy(self.PiLCFQDN)
            self.info_stream('Connected to PiLC: {:s}'.format(self.PiLCFQDN))
        except:
            self.error_stream('Could not connect to PiLC: {:s}'.format(self.PiLCFQDN))
            return    

    
# start the server
if __name__ == "__main__":
    PiLCTriggerGateGenerator.run_server()
