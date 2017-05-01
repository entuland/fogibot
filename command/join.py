""" tells the bot to join the [params] channel """

class Command():
    
    def run(self):
        if self.owner == self.sender:
            self.response = f"attempting to join {self.params}"
            self.raw_send = "JOIN " + self.params
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"