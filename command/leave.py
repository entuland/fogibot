""" tells the bot to leave the [params] channel - optionally, append ': [reason]' """

class Command:
    
    owner_command = True
    
    def run(self):
        self.response = f"attempting to leave {self.params}"
        self.raw_send = "PART " + self.params
