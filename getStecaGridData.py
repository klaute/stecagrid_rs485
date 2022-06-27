
import struct
import serial # pip3 install pyserial

DEBUG = False

SERIAL_DEVICE   = "/dev/ttyUSB0"
SERIAL_BYTES    = 8
SERIAL_PARITY   = 'N'
SERIAL_SBIT     = 1
SERIAL_BAUDRATE = 38400
SERIAL_TIMEOUT  = 1

# 16 byte modbus rs845 response to read AC power of steca grid
#  HEX array to request ACpower from StacaGrid:
#  02 01 00 10 01 C9 65 40 03 00 01 29 7E 29 BE 03
#  Example of a StecaGrid answer:
#  02 01 00 1F C9 01 84 41 00 00 10 29 00 00 08 41 43 50 6F 77 65 72 3A 0B A2 78 85 FB 49 4C 03
SG_AC_POWER_RESPONSE = [
        0x02, #   2 = 
        0x01, #   1 = 
        0x00, #   0 = 
        0x10, #  16 = 
        0x01, #   1 = 
        0xC9, # 201 = 
        0x65, # 101 = 
        0x40, #  64 = 
        0x03, #   3 = 
        0x00, #   0 = 
        0x01, #   1 = 
        0x29, #  41 = 
        0x7E, # 126 = 
        0x29, #  41 = 
        0xBE, # 190 = 
        0x03  #   3 = 
    ]

port = serial.Serial(baudrate=SERIAL_BAUDRATE, port=SERIAL_DEVICE, timeout=SERIAL_TIMEOUT, parity=SERIAL_PARITY, stopbits=SERIAL_SBIT, bytesize=SERIAL_BYTES, xonxoff=0, rtscts=0)


def getStecaGridACPower():

  with port as s:
    if DEBUG:
        print("response " + str(SG_AC_POWER_RESPONSE))

    s.write(SG_AC_POWER_RESPONSE)

    in_data = s.read(size=31)
    if DEBUG:
        print("data " + str(in_data))
        i = 0
        for d in in_data:
            print(str(i) + " " + str(in_data[i]) + " " + chr(in_data[i]) + " 0x%02x" % in_data[i])
            i = i + 1

    if len(in_data) < 31:
        # TODO error handling here
        return 0

    if in_data[23] == 0x0B:
        # AC power is > 0
        iacpower = ((in_data[26] << 8 | in_data[24]) << 8 | in_data[25]) << 7 # formula to float - conversion according to Steca

        if DEBUG:
            print("iacpower 0x%0X" % iacpower)
            print("iacpower " + str(iacpower))
            print("in_data[24-27] 0x%02x%02x%02x" % (in_data[24] , in_data[25] , in_data[26]))

        tmp_data = [ 0, int(in_data[24]), int(in_data[25]), int(in_data[26]) ]

        facpower, = struct.unpack('f', struct.pack('I', iacpower))

        if DEBUG:
            print(facpower)

        return facpower

    elif in_data[23] == 0x0C:
        # AC power is 0
        return 0

    else:
        # TODO error handling, received data is incorrect
        return 0

if __name__ == "__main__":

    ac_power = getStecaGridACPower()

    print(int(ac_power))

    port.close()

