from mycroft import MycroftSkill, intent_handler
from datetime import date, timedelta, datetime, time, tzinfo
import os

"""
Print support Mycroft Skill
"""

class Print(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.printdev = ""

    def initialize(self):
        self.add_event('configuration.updated', self.handler_configuration_updated)
        self.load_configuration()
        self.register_entity_file('target.entity')

    def stop(self):
        pass

    def shutdown(self):
        pass

    def handler_configuration_updated(self, message):
        self.load_configuration()
        self.log.info("Configuration has been reloaded.")
        return

    def load_configuration(self):
        self.printdev = self.settings.get('printdev')
        self.log.info("Printer device is: " + str(self.printdev))
        return

    """
    Handle intents
    """
    @intent_handler('print.intent')
    def handler_print(self, message):
        self.log.debug("Running print handler....")	
        """ Fetch the target from the message """
        target = message.data.get('target')
        self.print_out(target)
##        if target is None:
##            self.log.debug("Could not identify the target system to be queried. Defaulting to 'system'.")
##            if self.chatterbox:
##                self.speak("I didn't understand the target to be checked. Defaulting to system.")
##            target = "system"

##        result = self.fetch_status(target)
##        self.log.debug(result)

        
    def print_out(self, message):
        self.log.debug("Printing....")        
        #cmd = 'echo "test test test' + str(target) + '"'
        cmd = 'echo "test test test" >> ' + self.printdev
        returned_value = os.system(cmd)  # returns the exit code in unix
        self.log.debug("Returned value:" + str(returned_value))




def create_skill():
    return Print()