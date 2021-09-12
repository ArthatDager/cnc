import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    #parity=serial.PARITY_ODD,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
#   CR = '\r'
#   EIGHTBITS = 8
#   FIVEBITS = 5
#   LF = '\n'
#   PARITY_EVEN = 'E'
#   PARITY_MARK = 'M'
#   PARITY_NAMES = {'E': 'Even', 'M': 'Mark', 'N': 'None', 'O': 'Odd', 'S'...
#   PARITY_NONE = 'N'
#   PARITY_ODD = 'O'
#   PARITY_SPACE = 'S'
#   SEVENBITS = 7
#   SIXBITS = 6
#   STOPBITS_ONE = 1
#   STOPBITS_ONE_POINT_FIVE = 1.5
#   STOPBITS_TWO = 2
#   VERSION = '3.4'
#   XOFF = '\x13'

ser.isOpen()

print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

input=1
while 1 :
    # get keyboard input
    input = raw_input(">> ")
        # Python 3 users
        # input = input(">> ")
    if input == 'exit':
        ser.close()
        exit()
    else:
        # send the character to the device
        # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
        ser.write(input + '\r\n')
        out = ''
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(1)
        while ser.inWaiting() > 0:
            out += ser.read(1)

        if out != '':
            print ">>" + out
