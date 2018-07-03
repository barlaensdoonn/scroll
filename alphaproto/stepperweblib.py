# !/usr/bin/python2.7
import urllib2
#  import urllib
import httplib
import struct
import time
#  import sys


class StepperComms:
    # Type Matters, only listed in Documentation or Object Directory

    # Signed 16 (short)
    TypeS16 = 0
    # Unsigned 16 (unsigned short)
    TypeU16 = 1
    # Signed32 (int)
    TypeS32 = 2
    # Unsigned 32 (uint)
    TypeU32 = 3
    # Signed 8 bit (char)
    TypeS08 = 4
    # Unsigned 8 bit (uchar)
    TypeU08 = 5

    def MakeUrl(self, Host, Index, SubIndex):
        url = "http://%s/od/%04X/%02X" % (Host, Index, SubIndex)
        return url

    def MakeValue(self, Value, Type):
        svalue = ""
        if Type == self.TypeS16:
            s = struct.pack(">h", Value)
            c = struct.unpack("<BB", s)
            svalue = '"%02X%02X"' % (c)
        elif Type == self.TypeU16:
            s = struct.pack(">H", Value)
            c = struct.unpack("<BB", s)
            svalue = '"%02X%02X"' % (c)
        elif Type == self.TypeS32:
            s = struct.pack(">i", Value)
            c = struct.unpack("<BBBB", s)
            svalue = '"%02X%02X%02X%02X"' % (c)
        # unsigned only
        elif Type == self.TypeU32:
            s = struct.pack(">I", Value)
            c = struct.unpack("<BBBB", s)
            svalue = '"%02X%02X%02X%02X"' % (c)
        elif Type == self.TypeS08:
            s = struct.pack(">b", Value)
            c = struct.unpack("<B", s)
            svalue = '"%02X"' % (c)
        elif Type == self.TypeU08:
            s = struct.pack(">B", Value)
            c = struct.unpack("<B", s)
            svalue = '"%02X"' % (c)
        return svalue

    def SetRegister(self, Host, Index, SubIndex, Value, Type):
        # Create URL scheme
        url = self.MakeUrl(Host, Index, SubIndex)
        # Motor controller needs 1.0 not 1.0
        httplib.HTTPConnection._http_vsn = 10
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
        # Value needs to be in Hex with quotes
        svalue = self.MakeValue(Value, Type)
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
        time.sleep(.1)

    def GetRegister(self, Host, Index, SubIndex):
        # Create URL scheme
        url = self.MakeUrl(Host, Index, SubIndex)
        # Motor controller needs 1.0 not 1.0
        httplib.HTTPConnection._http_vsn = 10
        httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        # on get, open url
        response = urllib2.urlopen(url)
        # Get response (should be hex in quotes)
        html = response.read()
        # print html
        response.close()
        # Value is retruns in quotes, strip
        svalue = html.strip('"')
        # Convert to actual int
        # Sign might matter here, check
        # print svalue
        Value = int(svalue, 16)
        return Value


class StepperControl:
    ControlWord = 0x6040
    StatusWord = 0x6041
    ProfileVelocity = 0x6081
    TargetPosition = 0x607A
    Inputs = 0x60FD
    ActualPosition = 0x6064
    OperatingMode = 0x6060
    InputVoltageRange = 0x3240

    def __init__(self, Host):
        self.host = Host
        # Create comms
        self.comms = StepperComms()
        # Set Input 1 to 24 Volt Range
        self.comms.SetRegister(self.host, self.InputVoltageRange, 0x06, 1, self.comms.TypeU32)
        # Set As Position Mode
        self.comms.SetRegister(self.host, self.OperatingMode, 0x00, 1, self.comms.TypeU08)

    # Speed between 0 and 250 (positive only)
    # Already ramps up and down, max speed
    # Position negative and positive
    def MoveRelative(self, Speed, Steps):
        # Set speed as unsigned number
        self.comms.SetRegister(self.host, self.ProfileVelocity, 0, Speed, self.comms.TypeU32)
        # Set relative position in ticks (25000 = 1 revolution of motor shaft)
        self.comms.SetRegister(self.host, self.TargetPosition, 0, Steps, self.comms.TypeS32)

        # Bit 4 start
        # Bit 5 immediate
        # Bit 6 Absolute 0 vs Relative 1
        # Bit 8 halt
        # Bit 9 speed is not changed until target, no braking?
        # must be moved to completely

        # Quick Stop, Enable Voltage
        self.comms.SetRegister(self.host, self.ControlWord, 0, 0x06, self.comms.TypeU16)
        # Switch On
        self.comms.SetRegister(self.host, self.ControlWord, 0, 0x07, self.comms.TypeU16)
        # Enable Operation, Set Relative Motion
        self.comms.SetRegister(self.host, self.ControlWord, 0, 0x4F, self.comms.TypeU16)
        # Start
        self.comms.SetRegister(self.host, self.ControlWord, 0, 0x5F, self.comms.TypeU16)

    # Halt and clear everything?
    def MotorHalt(self):
        self.comms.SetRegister(self.host, self.ControlWord, 0, 0x1000, self.comms.TypeU16)

    def CheckReached(self):
        # In status? 0x6041
        # Bit 10 Target Reached
        # Bit 12 Point Acknowledged

        reach = self.comms.GetRegister(self.host, self.StatusWord, 0)
        if reach & 0x0400:
            return 1
        else:
            return 0

    def CheckFlag(self):
        flag = self.comms.GetRegister(self.host, self.Inputs, 0)
        # print flag
        if flag & 0x10000 == 0:
            return 1
        else:
            return 0
