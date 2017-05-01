""" tells the bot to quit the network with message [params] """

class Command():
    
    def run(self):
        if self.owner == self.sender:
            self.quit = True
            reason = self.params.strip()
            if not reason:
                reason = "quitting"
            self.raw_send = "QUIT :" + reason
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"