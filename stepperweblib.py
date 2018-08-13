#!/usr/bin/python
# classes to communicate with Nanotech N5-1-3 motor controller via REST API
# authored by Gary Stein at AlphaProto June 2018
# refactored by Brandon Aleson July 2018
# updated 8/3/18

import urllib2
import urllib
import httplib
import struct
import time
import sys


class StepperComms:
    # type matters; only listed in documentation or object directory

    # Signed 16 (short)
    typeS16 = 0
    # Unsigned 16 (unsigned short)
    typeU16 = 1
    # Signed32 (int)
    typeS32 = 2
    # Unsigned 32 (uint)
    typeU32 = 3
    # Signed 8 bit (char)
    typeS08 = 4
    # Unsigned 8 bit (uchar)
    typeU08 = 5

    def make_url(self, host, index, subindex):
        url = "http://%s/od/%04X/%02X" % (host, index, subindex)
        return url

    def make_value(self, value, type):
        svalue = ""
        if(type == self.typeS16):
            s = struct.pack(">h", value)
            c = struct.unpack("<BB", s)
            svalue = '"%02X%02X"' % (c)
        elif(type == self.typeU16):
            s = struct.pack(">H", value)
            c = struct.unpack("<BB", s)
            svalue = '"%02X%02X"' % (c)
        elif(type == self.typeS32):
            s = struct.pack(">i", value)
            c = struct.unpack("<BBBB", s)
            svalue = '"%02X%02X%02X%02X"' % (c)
        # unsigned only
        elif(type == self.typeU32):
            s = struct.pack(">I", value)
            c = struct.unpack("<BBBB", s)
            svalue = '"%02X%02X%02X%02X"' % (c)
        elif(type == self.typeS08):
            s = struct.pack(">b", value)
            c = struct.unpack("<B", s)
            svalue = '"%02X"' % (c)
        elif(type == self.typeU08):
            s = struct.pack(">B", value)
            c = struct.unpack("<B", s)
            svalue = '"%02X"' % (c)
        return svalue

    def set_register(self, host, index, subindex, value, type):
        # Create URL scheme
        url = self.make_url(host, index, subindex)

        # Motor controller needs 1.0 not 1.0
        # httplib.HTTPConnection._http_vsn = 10
        # httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        # value needs to be in Hex with quotes
        svalue = self.make_value(value, type)
        request = urllib2.Request(url)
        # Add to request
        request.add_data(svalue)
        # Send to server
        response = urllib2.urlopen(request)
        # response empty on success, check?
        # html = response.read()
        # print html
        response.close()
        # Recommends wait after every command
        time.sleep(.01)

    def get_register(self, host, index, subindex):
        # Create URL scheme
        url = self.make_url(host, index, subindex)

        # Motor controller needs 1.0 not 1.0
        # httplib.HTTPConnection._http_vsn = 10
        # httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        # on get, open url
        response = urllib2.urlopen(url)
        # Get response (should be hex in quotes)
        html = response.read()
        # print html
        response.close()
        # value is retruns in quotes, strip
        svalue = html.strip('"')
        # Convert to actual int
        # Sign might matter here, check
        # print svalue
        value = int(svalue, 16)
        return value


class StepperControl:
        ControlWord = 0x6040
        StatusWord = 0x6041
        ProfileVelocity = 0x6081
        TargetPosition = 0x607A
        Inputs = 0x60FD
        ActualPosition = 0x6064
        OperatingMode = 0x6060
        InputVoltageRange = 0x3240
        ClosedLoop = 0x3202

        def __init__(self, host):
            self.host = host
            # Create comms
            self.comms = StepperComms()
            # Set Input 1 to 24 Volt Range
            self.comms.set_register(self.host, self.InputVoltageRange, 0x06, 1, self.comms.typeU32)
            # Set As Position Mode
            self.comms.set_register(self.host, self.OperatingMode, 0x00, 1, self.comms.typeU08)

        # Speed between 0 and 250 (positive only)
        # Already ramps up and down, max speed
        # Position negative and positive
        def move_relative(self, Speed, Steps):
            # Set speed as unsigned number
            self.comms.set_register(self.host, self.ProfileVelocity, 0, Speed, self.comms.typeU32)
            # Set relative position in ticks (25000 = 1 revolution of motor shaft)
            self.comms.set_register(self.host, self.TargetPosition, 0, Steps, self.comms.typeS32)

            # Bit 4 start
            # Bit 5 immediate
            # Bit 6 Absolute 0 vs Relative 1
            # Bit 8 halt
            # Bit 9 speed is not changed until target, no braking?
            # must be moved to completely

            # Quick Stop, Enable Voltage
            self.comms.set_register(self.host, self.ControlWord, 0, 0x06, self.comms.typeU16)
            # Switch On
            self.comms.set_register(self.host, self.ControlWord, 0, 0x07, self.comms.typeU16)
            # Enable Operation, Set Relative Motion
            self.comms.set_register(self.host, self.ControlWord, 0, 0x4F, self.comms.typeU16)
            # Start
            self.comms.set_register(self.host, self.ControlWord, 0, 0x5F, self.comms.typeU16)

        # Halt and clear everything?
        def halt(self):
            # Halt Free Spin
            # self.comms.set_register(self.host, self.ControlWord, 0, 0x1000, self.comms.typeU16)
            # Halt powered?
            # self.comms.set_register(self.host, self.ControlWord, 0, 0x1007, self.comms.typeU16)

            # Cancel move
            self.comms.set_register(self.host, self.ControlWord, 0, 0x0007, self.comms.typeU16)
            # Hold
            self.comms.set_register(self.host, self.ControlWord, 0, 0x000F, self.comms.typeU16)

            # Move Zero?
            # self.move_relative(0, 0)

        def check_reached(self):
            # In status? 0x6041
            # Bit 10 Target Reached
            # Bit 12 Point Acknowledged

            reach = self.comms.get_register(self.host, self.StatusWord, 0)
            if(reach & 0x0400):
                return 1
            else:
                return 0

        def check_flag(self):
            flag = self.comms.get_register(self.host, self.Inputs, 0)
            # print flag
            return 1 if(flag & 0x10000 == 0) else 0

        def get_status(self):
            v = self.comms.get_register(self.host, self.StatusWord, 0)
            # print "%04X" % (v)
            print(v)

        def get_closed(self):
            v = self.comms.get_register(self.host, self.ClosedLoop, 0)
            # print "%04X" % (v)
            print(v)
