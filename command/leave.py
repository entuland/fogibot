""" tells the bot to leave the [params] channel - optionally, append ': [reason]' """

class Command():
    
    def run(self):
        if self.owner == self.sender:
            self.response = f"attempting to leave {self.params}"
            self.raw_send = "PART " + self.params
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"