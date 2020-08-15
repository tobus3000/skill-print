from mycroft import MycroftSkill, intent_handler
from datetime import date, timedelta, datetime, time, tzinfo
import os

"""
Print support Mycroft Skill
"""

class Print(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.print_dev = ""
        self.print_all = False
        self.bucket_size = 50
        self.msg_bucket = []

    def initialize(self):
        self.add_event('speak', self.handler_speak)
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
        self.print_dev = self.settings.get('printdev')
        self.print_all = self.settings.get('printall', False)
        self.bucket_size = self.settings.get('bucketsize', 50)

        self.log.info("Printer device is: " + str(self.print_dev))
        self.log.debug("Print out everything is set to: " + str(self.print_all))
        self.log.debug("Past messages bucket size: " + str(self.bucket_size))
        return


    def bucket_add(self, message):
        today = date.today()
        if self.bucket_size <= len(self.msg_bucket):
            del(self.msg_bucket[0]) 
        self.msg_bucket.append((today, message))

    def bucket_get(self, message, amount):
        pass


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

    def handler_speak(self, message):
        self.bucket_add(message)
        if self.print_all:
            self.print_out(format(message.data.get('utterance'))) 
        else:
            self.log.debug("Skipping printout of message.")

        
    def print_out(self, target):
        today = date.today()
        self.log.debug("Printing....") 
        cmd_ts = 'echo "' + str(today) + ':" >> ' + self.print_dev
        exit_code = os.system(cmd_ts)
        if exit_code == 0: 
            cmd = 'echo "' + str(target) + '" >> ' + self.print_dev
            returned_value = os.system(cmd)  # returns the exit code in unix
        else:
            self.speak_dialog('error')
        self.log.debug("Returned value:" + str(returned_value))





def create_skill():
    return Print()