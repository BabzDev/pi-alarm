import RPi.GPIO as GPIO
import time

class keypad():

    MATRIX = [  [1,2,3,'A'],
                [4,5,6,'B'],
                [7,8,9,'C'],
                ['*',0,'#','D']]

    ROW = [31,33,35,37]
    COL = [32,36,38,40]

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

    def GPIO_setup_pins(self):
        for j in range(4):
            GPIO.setup(self.COL[j], GPIO.OUT)
            GPIO.output(self.COL[j], 1)

        for i in range(4):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    def GPIO_clean_up(self):
        GPIO.cleanup()

    def get_input(self):
        self.GPIO_setup_pins()
        try:
            while(True):
                for j in range(4):
                    GPIO.output(self.COL[j], 0)
                    for i in range(4):
                        if GPIO.input(self.ROW[i]) == 0:
                            while (GPIO.input(self.ROW[i])==0):
                                pass
                            return self.MATRIX[i][j]
                    GPIO.output(self.COL[j], 1)
                #Because of the nature infitie loop and waiting for input, I have put the process to sleep for 1 milliseconds.
                #This should permit to read inputs correctly, and not maximise 100% of the cpu
                time.sleep(0.001)
        except KeyboardInterrupt:
            self.GPIO_clean_up()