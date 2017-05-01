""" tells the bot to join the [params] channel """

class Command:
    
    owner_command = True
    
    def run(self):
        self.response = f"attempting to join {self.params}"
        self.raw_send = "JOIN " + self.params
