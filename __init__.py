from mycroft import MycroftSkill, intent_handler
#from datetime import date, timedelta, datetime, time, tzinfo
from datetime import datetime, timezone
import pytz 
import subprocess
import re

"""
Print support Mycroft Skill
"""

class Print(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.printer_active = False
        self.print_dev = ""
        self.print_time = True
        self.print_all = False
        self.print_lf = False
        self.bucket_size = 50
        self.msg_bucket = []

    def initialize(self):
        self.add_event('speak', self.handler_speak)
        self.settings_change_callback = self.load_configuration
        self.load_configuration()
        self.register_entity_file('target.entity')
        self.register_entity_file('action.entity')
        self.register_entity_file('amount.entity')

    def stop(self):
        pass

    def shutdown(self):
        pass

    def load_configuration(self):
        self.printer_active = self.settings.get('printeractive', False)
        self.print_dev = self.settings.get('printdev')
        self.print_all = self.settings.get('printall', False)
        self.print_lf = self.settings.get('printlf', False)
        self.print_time = self.settings.get('printtime', True)
        self.bucket_size = self.settings.get('bucketsize', 50)
        if self.__valid_printdev(self.print_dev):
            self.log.info("Printer device is: " + str(self.print_dev))
            self.log.debug("Print out everything is set to: " + str(self.print_all))
            self.log.debug("Past messages bucket size: " + str(self.bucket_size))
        else:
            self.disable_printer()
            self.log.info("Printer device seems to be invalid.")
            self.log.debug("Print out everything is set to: " + str(self.print_all))
            self.log.debug("Print out everything is set to: " + str(self.print_all))
        return


    def bucket_add(self, message):
        #today = datetime.now()
        today = "testdate"
        if self.bucket_size <= len(self.msg_bucket):
            del(self.msg_bucket[0]) 
        self.msg_bucket.append((today, message))

    def bucket_get(self, message, amount):
        pass

    def enable_printer(self):
        self.printer_active = True
        self.settings['printeractive'] = True
        return

    def disable_printer(self):
        self.printer_active = False
        self.settings['printeractive'] = False
        return

    def enable_linefeed(self):
        self.print_lf = True
        self.settings['printlf'] = True
        return

    def disable_linefeed(self):
        self.print_lf = False
        self.settings['printlf'] = False
        return

    """ Generic regex check returning True/False """
    def __regex_match(self, chk_strg, search=re.compile(r'[^/a-z0-9.]').search):
        return not bool(search(chk_strg))


    """ Some checking to avoid shell command injection and to make sure the device is active. """
    def __valid_printdev(self, printdev):
        if self.__regex_match(printdev):
            """ There's not too much garbage in the string, thus giving it a shot to see if it exists..."""
            res_obj = subprocess.run(["file", printdev], check=True, timeout=1)
            if res_obj.returncode == 0:
                self.log.info("Valid printer.")
                return True
        self.log.error("Configured printer device is invalid.")
        return False
        

    def __is_number(self, s):
        if s is None:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    """
    Handle intents
    """
    @intent_handler('print.intent')
    def handler_print(self, message):
        self.log.debug("Running print handler....")	
        """ Fetch the target from the message """
        target = message.data.get('target')
        amount = message.data.get('amount')
        if target == "linefeed" or target == "feed":
            self.disable_linefeed()
            self.print_out(" ")
            self.enable_linefeed()
        
        if self.__is_number(amount):
            self.print_out("TESTING AMOUNT: " + str(amount))
            
        if target == "buffer":
            for msg_item in self.msg_bucket:
                self.log.debug(str(msg_item))
                self.print_out("TESTING ALL BUFFER: " + str(msg_item))


    @intent_handler('printerconfig.intent')
    def handler_config(self, message):
        self.log.debug("Running config handler....")
        action = message.data.get('action')
        target = message.data.get('target')
        if action is None:
            self.speak("I did not understand. Please repeat.")
            return
        
        if target is None:
            self.speak("I didn't catch the target. Can you please repeat?")
            return

        if action == "enable" or action == "activate":
            if target == "printer":
                self.speak("Enabling printer.")
                self.enable_printer()
                
            elif target == "linefeed":
                self.speak("Enabling linefeed.")
                self.enable_linefeed()

        elif action == "disable" or action == "deactivate":
            if target == "printer":
                self.speak("Disabling printer.")
                self.disable_printer()

            elif target == "linefeed":
                self.speak("Disabling linefeed.")
                self.disable_linefeed()

    def handler_speak(self, message):
        self.bucket_add(message)
        if self.printer_active:
            if self.print_all:
                try:
                    self.print_out(format(message.data.get('utterance'))) 
                except:
                    self.log.error("Failed to print.")
                    self.disable_printer()

            else:
                self.log.debug("Skipping printout of message.")
        else:
            self.log.debug("Skipping printout because printer is not active.")


    def __print(self, msg):
        try:
            printdev = open(self.print_dev, "a")
        except:
            self.log.error("Could not start printer commnunication.")
            self.disable_printer()
            return False
        
        try:
            spobj = subprocess.run(['echo', msg], stdout=printdev, check=True, timeout=1)
        except:
            self.log.error("Failed to send message to printer.")
            self.disable_printer()
            return False
        printdev.close()
        return True

    def print_out(self, msg):
        if self.__valid_printdev(self.print_dev) is False:
            return

        self.log.debug("Printing...")
        if self.print_time and self.printer_active:
            tz = pytz.timezone(self.location_timezone)
            cur_time_obj = datetime.now(tz)
            print_time = cur_time_obj.strftime('%d.%m.%Y %H:%M:%S %Z %z')
            if self.__print(str(print_time)) is False:
                self.speak_dialog('error')
                self.disable_printer()
                
        if self.printer_active: 
            if self.__print(str(msg)) is False:
                self.speak_dialog('error')
                self.disable_printer()

        if self.printer_active and self.print_lf:
            self.log.debug("Printing line feed.")
            if self.__print(" ") is False:
                self.speak_dialog('error')
                self.disable_printer()





def create_skill():
    return Print()