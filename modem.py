import serial

class gsm_modem():

    def __init__(self):
        self.port = serial.Serial("/dev/ttyS0",baudrate=9600,timeout=1)

    def make_call(self, phone_number) :
        self.port.write(b'ATD' + phone_number + b';\r')
        print(self.port.read(30))

    def hang_up(self):
        self.port.write(b'ATH\r')
        self.port.read(30)