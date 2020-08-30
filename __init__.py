from mycroft import MycroftSkill, intent_handler
#from datetime import date, timedelta, datetime, time, tzinfo
from datetime import datetime, timezone
import pytz 
import subprocess
import re
import time

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
        else:
            self.printer_disable()
        
        self.log.debug("Print out everything is set to: " + str(self.print_all))
        self.log.debug("Past messages bucket size: " + str(self.bucket_size))            
        return


    def bucket_add(self, message):
        if self.bucket_size <= len(self.msg_bucket):
            del self.msg_bucket[0] 
        self.msg_bucket.append((self.__get_datetime(), message))

    def printer_status(self):
        status = "disabled"
        if self.printer_active:
            status = "enabled"
        self.speak_dialog('status', data={"target": "printer", "status": status})
        if self.print_all is False and self.printer_active():
            self.__print("The printer is " + status + ".")
        return

    def printer_enable(self):
        self.printer_active = True
        self.settings['printeractive'] = True
        return

    def printer_disable(self):
        self.printer_active = False
        self.settings['printeractive'] = False
        return

    def linefeed_status(self):
        status = "disabled"
        if self.print_lf:
            status = "enabled"
        self.speak_dialog('status', data={"target": "linefeed", "status": status})
        if self.print_all is False and self.printer_active():
            self.__print("Linefeed is " + status + ".")

    def linefeed_enable(self):
        self.print_lf = True
        self.settings['printlf'] = True
        return

    def linefeed_disable(self):
        self.print_lf = False
        self.settings['printlf'] = False
        return

    """ Private: Get a nice date/time string """
    def __get_datetime(self):
        tz = pytz.timezone(self.location_timezone)
        cur_time_obj = datetime.now(tz)
        return str(cur_time_obj.strftime('%d.%m.%Y %H:%M:%S %Z %z'))

    """ Private: Generic regex check returning True/False """
    def __regex_match(self, chk_strg, search=re.compile(r'[^/a-z0-9.]').search):
        return not bool(search(chk_strg))


    """ Private: Some checking to avoid shell command injection and to make sure the device is active. """
    def __valid_printdev(self, printdev):
        if self.__regex_match(printdev):
            """ There's not too much garbage in the string, thus giving it a shot to see if it exists..."""
            try:
                subprocess.run(["ls", printdev], stdout=subprocess.DEVNULL, check=True, timeout=1)
                return True
            except:
                self.printer_disable()
        self.log.error("Configured printer device is invalid.")
        return False
        
    """ Private: Simple check to see if string is a number... """
    def __is_number(self, s):
        if s is None:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    """ Private: Send message to printer device """
    def __print(self, msg):
        self.log.debug("Printing line for message: " +str(msg))
        if self.printer_active is False:
            self.log.debug("Printer is not active.")
            return False

        if self.__valid_printdev(self.print_dev) is False:
            return False

        try:
            printdev = open(self.print_dev, "a")
        except:
            self.printer_disable()
            self.log.error("Could not start printer communication.")
            return False
        
        try:
            subprocess.run(['echo', msg], stdout=printdev, check=True, timeout=1)
        except:
            self.printer_disable()
            self.log.error("Failed to send message to printer.")
            return False
        printdev.close()
        return True


    """ Public: Prepare and send message """
    def print_out(self, msg):
        self.log.debug("Starting print out.")
        if self.print_time:
            if self.__print(self.__get_datetime()) is False:
                self.speak_dialog('error')
                return False

        if self.__print(str(msg)) is False:
            self.speak_dialog('error')
            return False

        if self.print_lf:
            if self.__print(str(" ")) is False:
                self.speak_dialog('error')
                return False
        return True


    """
    Handle intents
    """
    @intent_handler('print.intent')
    def handler_print(self, message):
        self.log.debug("Running print.intent handler.")	
        """ Fetch the target from the message """
        target = message.data.get('target')
        amount = message.data.get('amount')
        
        """ Print an empty line... """
        if target in ["linefeed", "feed"]:
            self.__print(" ")

        """ Print a local time/date stamp """        
        if target in ["time", "date"]:
            self.__print(self.__get_datetime())

        """ Print the printer status """
        if target == "status":
            self.printer_status()

        if self.__is_number(amount):
            self.print_out("TESTING AMOUNT: " + str(amount))
            
        if target == "buffer":
            self.speak("Printing message buffer.")
            if len(self.msg_bucket) == 0:
                self.speak("The message buffer is empty.")
                return True
            else:
                for msg_item in self.msg_bucket:
                    (ts, msg) = msg_item
                    self.__print("@" + ts)
                    if msg is not None or msg != "":
                        self.__print(msg.data.get('utterance'))
                    else:
                        self.__print("blank message")
                    # TODO: Add locking on __print
                    time.sleep(1)




    @intent_handler('printerconfig.intent')
    def handler_config(self, message):
        self.log.debug("Running printerconfig.intent handler.")
        action = message.data.get('action')
        target = message.data.get('target')
        if action is None or target is None:
            self.speak_dialog('pleaserepeat')
            return

        if action in ["enable", "activate", "on"] and target == "printer":
            self.printer_enable()
        elif action in ["enable", "activate", "on"] and target in ["linefeed", "feed"]:
            self.linefeed_enable()
        elif action in ["disable", "deactivate", "off"] and target == "printer":
            self.printer_disable()
        elif action in ["disable", "deactivate", "off"] and target in ["linefeed", "feed"]:
            self.linefeed_disable()
        
        if target == "printer":
            self.printer_status()
        
        if target in ["linefeed", "feed"]:
            self.linefeed_status()


    def handler_speak(self, message):
        self.bucket_add(message)
        if self.printer_active:
            if self.print_all:
                try:
                    self.print_out(format(message.data.get('utterance'))) 
                except:
                    self.printer_disable()
                    self.log.error("Error while printing.")
                    self.speak_dialog('error')
            else:
                self.log.debug("Skipping printout of message.")
        else:
            self.log.debug("Skipping printout because printer is not active.")


def create_skill():
    return Print()