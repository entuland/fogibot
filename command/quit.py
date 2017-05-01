""" tells the bot to quit the network with message [params] """

class Command:
    
    owner_command = True
    
    def run(self):
        self.quit = True
        reason = self.params.strip()
        if not reason:
            reason = "quitting"
        self.raw_send = "QUIT :" + reason
