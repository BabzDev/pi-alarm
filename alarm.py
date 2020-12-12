import RPi.GPIO as GPIO
from output import logger
from keypad import keypad
import threading
import time

logger = logger()
keypad = keypad()

class alarm:
    def __init__(self, GPIO_pin):
        self.GPIO_pin = GPIO_pin
        self.__alarm_on = False
        # Alarm is armed when alarm is switched on and doors are closed.
        self.__alarm_armed = False
        self.__pin_code = ''
        self.__max_notifications = 2

        #Initiialize background tasks
        self.__background_tasks_status = False
        self.__init_threads()

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.GPIO_pin,GPIO.IN)
    
    def __init_threads(self):
        # Create threads for background task
        self.__init_thread_alam_monitoring()
        self.__init_thread_background_tasks()

    def __init_thread_background_tasks(self):
        self.__thread_background_tasks = threading.Thread(target = self.__background_tasks)
        self.__thread_background_tasks.daemon = True

    def __init_thread_alam_monitoring(self):
        self.__thread_alarm_monitoring = threading.Thread(target = self.__alarm_monitoring)              
        self.__thread_alarm_monitoring.daemon = True

    def is_alarm_on(self):
        return self.__alarm_on

    def alarm_menu(self):
        logger.output('Alarm Menu')
        logger.output('1. Set Alarm')
        logger.output('2. Disarm Alarm')
        logger.output('3. Change Pin')
        logger.output('*. Cancel')

        response = keypad.get_input()

        if response == 1:
            self.__set_alarm()
        elif response == 2:
            self.__disarm_alarm()
        elif response == 3:
            self.__change_pin_code()
        elif response == '*':
            pass
        else:
            logger.output('Not a valid entry')

    def __is_circuit_open(self):
        if GPIO.input(self.GPIO_pin) == 0:
            return True
        else:
            return False


    def __get_pin_code(self):
    # Returns a pincode from user input or 'Cancelled'

        temp_pin = ''
        while  True:
            response = keypad.get_input()
            logger.output(response)

            # Admin button allows to cancel
            if response == 'A':
                logger.output('Admin')
                logger.output('Enter * to cancel, or any key to continue')
                response = keypad.get_input()
                if response == '*':
                    return 'Cancelled'
                else: 
                    logger.output('Continue with pin: ' + temp_pin)

            # Clear button
            elif response == '*':
                temp_pin = self.__clear_pin(temp_pin)
    
            # All other inputs except # are used as PIN.
            elif response != '#':
                temp_pin += str(response)
            else:
                logger.output('To confirm pin please press # again')
                response = keypad.get_input()
                if response == '#':
                    return temp_pin
                elif response == '*':
                    temp_pin = self.__clear_pin(temp_pin)
                else:
                    logger.output('Continue with pin: ' + temp_pin)

    def __get_pin_code2(self):
    # Gets the pin twice and confirms inputs match. Returns False if failed or cancelled

        logger.output('Enter Pin')

        #Gets the pin for 1st time and checks if the response is cancelled
        temp_pin = self.__get_pin_code()
        if self.__pin_entry_cancelled(temp_pin):
            logger.output('Pin entry Cancelled')
            return False
        else:   
            logger.output('Verify the pin again')

            #Gets the pin for 2nd time and checks if the response is cancelled
            temp_pin1 = self.__get_pin_code()
            if self.__pin_entry_cancelled(temp_pin1):
                logger.output('Pin entry Cancelled')
                return False
            
            elif temp_pin != temp_pin1:
            # Ensure pin is the same
                logger.output('Your PIN does not match!')
                return False
            else:
                return temp_pin

    def __change_pin_code(self):
        logger.output('Changing Pin')
        if self.__pin_code != "":
            looping = True
            while looping == True:
                logger.output('Exisitng Pin')
                current_pin = self.__get_pin_code()
                if self.__is_pin_correct(current_pin):
                    self.__set_pin_code()
                    looping = False
                elif self.__pin_entry_cancelled(current_pin):
                    looping = False
                else:
                    logger.output('Incorrect Pin')
        else:
            self.__set_pin_code()

    def __set_alarm(self):
        if self.__alarm_on == True:
            logger.output('Alarm is already set!')
        else:
            if self.__pin_code != '':
                self.__alarm_on = True
                logger.output('Alarm turned on')
            else:
                if self.__set_pin_code() == False:
                    logger.output('Alarm still off :(')
                else:
                    self.__alarm_on = True
                    logger.output('Alarm turned on')

    def __pin_entry_cancelled(self, pin):
        if pin == 'Cancelled':
            return True
        else: 
            return False



    #  Changes the pin code and Returns True if Pin change successfull 
    def __set_pin_code(self):
        temp_pin = self.__get_pin_code2()
        if temp_pin == False:
            return False
        else:
            if self.__validate_pin(temp_pin):
                self.__pin_code = temp_pin
                return True
            else:
                return False


    # Ensures the pin meets the criteria
    def __validate_pin(self, temp_pin):
        logger.output('Checking pin code')
        if temp_pin == 'Cancelled' or (temp_pin == '' and self.__pin_code != ''):
            logger.output("Pin entry Cancelled")
            return 'Cancelled'
        elif len(temp_pin) < 6:
            logger.output('Pin is not long enough')
            return False
        else:
            return True

    def __is_pin_correct(self,tmp_pin):
        if tmp_pin == self.__pin_code:
            return True
        else: 
            return False

    def __disarm_alarm(self):
        if self.__alarm_on == False:
            logger.output('Alarm is not set!')
        else:
            while self.__alarm_on == True:
                logger.output('Enter PIN to Disarm')
                tmp_pin = self.__get_pin_code()
                if self.__pin_entry_cancelled(tmp_pin):
                    logger.output('Pin entry Cancelled')
                    break
                else:
                    if self.__is_pin_correct(tmp_pin) == True:
                        self.__alarm_on = False
                        self.__alarm_armed = False
                        logger.output('Alarm Disarmed')
                    else:
                        logger.output('Wrong Pin try again')

    def __clear_pin(self, temp_pin):
    # Clear pin function which returns emtpy pin if cleared, or retunrs reminder of existing pin
        logger.output('To clear pin press * again, or press any key to continue')
        response = keypad.get_input()
        if response == '*':
            logger.output("Pin entry is reset")
            return  ''
        else:
            logger.output('Current entry: ' + temp_pin)
            return temp_pin

    def background_tasks_on(self, status):
    # Turns on/off background tasks for alarm
        self.__background_tasks_status = status
        # Only trigger background tasks if they weren't already running
        if (self.__thread_background_tasks.is_alive() == False) and status:
            logger.output('Background tasks are now On')
            self.__init_thread_background_tasks()
            self.__thread_background_tasks.start()
        else:
            logger.output('Background tasks already running')

    def __background_tasks(self):
    # Task which ensures background tasks stay active if triggered

        while self.__background_tasks_status:            
            # Run Alarm Monitoring only if not already on
            if self.__thread_alarm_monitoring.is_alive() == False:
                # Only turn on monitroing if alarm is switched on
                if self.is_alarm_on():
                    self.__init_thread_alam_monitoring()
                    self.__thread_alarm_monitoring.start()

            #For better power efficiency, put the proces to sleep for 1 millisecond
            time.sleep(0.001)
    
    def __alarm_monitoring(self):
    #Task to monitor alarm once it has been activated

        # If doors are open at time of monitoring being triggered allow for the doors to close
        logger.output('Alarm monitoring is on')
        if self.__is_circuit_open():
            logger.output('Alarm is not armed. Close the doors!')
            while self.__is_circuit_open():
                pass
                time.sleep(0.001)
        logger.output('Waiting 5 seconds for system to arm')

        # Extra time off to allow for misfiring between the closed switches
        time.sleep(5)

        logger.output('Alarm is armed!')
        self.__alarm_armed = True

        # begin monitoring for breach if alarm is switched on
        while self.is_alarm_on():
            if self.__is_circuit_open():
                self.__alarm_triggered()
                break
            time.sleep(0.001)

    def __alarm_triggered(self):
    # Function to call if alarm has been triggered

        print('Alarm triggered')
        print('20 Seconds to disarm')
        time.sleep(20)

        if self.is_alarm_on():
            time_count = 0
            notify_count = 0
            while self.is_alarm_on():
                logger.output('Alarm still triggered')
                self.__sound_siren(True)

                if time_count % 25 == 0 and notify_count < self.__max_notifications:
                    notify_count += 1
                    self.__notify_alarm_triggered()
                time.sleep(1)
                time_count += 1
                
        else:
            print('Alarm disarmed on time')
    
    def __notify_alarm_triggered(self):
        logger.output('Making a call')
    
    def __sound_siren(self, status):
        pass