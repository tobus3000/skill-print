from mycroft import MycroftSkill, intent_handler
#from datetime import date, timedelta, datetime, time, tzinfo
from datetime import datetime, timezone
import pytz 
import os

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
        self.add_event('configuration.updated', self.handler_configuration_updated)
        self.load_configuration()
        self.register_entity_file('target.entity')
        self.register_entity_file('action.entity')

    def stop(self):
        pass

    def shutdown(self):
        pass

    def handler_configuration_updated(self, message):
        self.load_configuration()
        self.log.info("Configuration has been reloaded.")
        return

    def load_configuration(self):
        self.printer_active = self.settings.get('printeractive', False)
        self.print_dev = self.settings.get('printdev')
        self.print_all = self.settings.get('printall', False)
        self.print_lf = self.settings.get('printlf', False)
        self.print_time = self.settings.get('printtime', True)
        self.bucket_size = self.settings.get('bucketsize', 50)

        self.log.info("Printer device is: " + str(self.print_dev))
        self.log.debug("Print out everything is set to: " + str(self.print_all))
        self.log.debug("Past messages bucket size: " + str(self.bucket_size))
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

    """
    Handle intents
    """
    @intent_handler('print.intent')
    def handler_print(self, message):
        self.log.debug("Running print handler....")	
        """ Fetch the target from the message """
        target = message.data.get('target')
        amount = message.data.get('amount')
        self.print_out(target)
##        if target is None:
##            self.log.debug("Could not identify the target system to be queried. Defaulting to 'system'.")
##            if self.chatterbox:
##                self.speak("I didn't understand the target to be checked. Defaulting to system.")
##            target = "system"

##        result = self.fetch_status(target)
##        self.log.debug(result)

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
                self.speak("Enabling line feed.")
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
        if self.print_all:
            self.print_out(format(message.data.get('utterance'))) 
        else:
            self.log.debug("Skipping printout of message.")

        
    def print_out(self, target):
        self.log.debug("Printing...")
        if self.print_time and self.printer_active:
            tz = pytz.timezone(self.location_timezone)
            cur_time_obj = datetime.now(tz)
            print_time = cur_time_obj.strftime('%d.%m.%Y %H:%M:%S %Z %z')
            cmd_ts = 'echo "' + str(print_time) + '" >> ' + self.print_dev
            exit_code = os.system(cmd_ts)
            if exit_code != 0:
                self.speak_dialog('error')
                self.disable_printer()
                
        #cmd_ts = 'echo "' + str(print_time) + ':" >> ' + self.print_dev
        #exit_code = os.system(cmd_ts)
        if self.printer_active: 
            cmd = 'echo "' + str(target) + '" >> ' + self.print_dev
            exit_code = os.system(cmd)  # returns the exit code in unix
            if exit_code != 0:
                self.speak_dialog('error')
                self.disable_printer()

            #self.log.debug("Returned value:" + str(exit_code))
        if self.printer_active and self.print_lf:
            cmd = 'echo " " >> ' + self.print_dev
            exit_code = os.system(cmd)
            if exit_code != 0:
                self.speak_dialog('error')
                self.disable_printer()





def create_skill():
    return Print()