from mycroft import MycroftSkill, intent_handler
#from datetime import date, timedelta, datetime, time, tzinfo
from datetime import datetime, timezone
import pytz 
import os
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
        if self.is_valid_printdev(self.print_dev):
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

    """ Some checking to avoid shell command injection and to make sure the device is active. """
    def is_valid_printdev(self, printdev):
        cmd = "file " + self.print_dev
        exit_code = os.system(cmd)
        self.log.debug("EXIT CODE: " + str(exit_code))
        #device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        #df = subprocess.check_output("lsusb")
        #devices = []
        #for i in df.split('\n'):
        #    if i:
        #        info = device_re.match(i)
        #        if info:
        #            dinfo = info.groupdict()
        #            dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
        #            devices.append(dinfo)
        #self.log.debug(str(df));
        return True

    """
    Handle intents
    """
    @intent_handler('print.intent')
    def handler_print(self, message):
        self.log.debug("Running print handler....")	
        """ Fetch the target from the message """
        target = message.data.get('target')
        amount = message.data.get('amount')
        utterance = message.data.get('utterance')
        if target == "linefeed":
            self.disable_linefeed()
            self.print_out(" ")
            self.enable_linefeed()
        
        if float(amount):
            self.print_out("TESTING AMOUNT: " + str(amount))
            
        if utterance == "print message buffer.":
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

        
    def print_out(self, target):
        self.is_valid_printdev(self.print_dev)
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
                
        if self.printer_active: 
            cmd = 'echo "' + str(target) + '" >> ' + self.print_dev
            exit_code = os.system(cmd)  # returns the exit code in unix
            if exit_code != 0:
                self.speak_dialog('error')
                self.disable_printer()

        if self.printer_active and self.print_lf:
            self.log.debug("Printing line feed.")
            cmd = 'echo " " >> ' + self.print_dev
            exit_code = os.system(cmd)
            if exit_code != 0:
                self.speak_dialog('error')
                self.disable_printer()





def create_skill():
    return Print()