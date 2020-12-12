from keypad import keypad
from Modem import gsm_modem
from alarm import alarm
import time

alarm = alarm(16)


class menu_interface():

    def __init__(self):
        self.modem = gsm_modem()
        self.keypad = keypad()

    def run(self):
        alarm.background_tasks_on(True)
        while True:
            if alarm.is_alarm_on() == True:
                print('Waiting for action')
                self.menu_awaiting_input()
            else:
                print('Waiting for action')
                self.menu_awaiting_input()
                
    def menu_awaiting_input(self):
        response = ''
        while response != 'A#':
            response = self.keypad.get_input()
            print(response)
            if response == 'A':
                response = self.keypad.get_input()
                if self.keypad.get_input() == '#':
                    response = 'A#'
                    alarm.alarm_menu()
                else: 
                    print(response)

menu = menu_interface()

menu.run()