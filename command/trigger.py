"""
    changes the bot's trigger to [params] (alphanumeric chars only)
"""

class Command():
    
    def run(self):
        if self.owner == self.sender:
            trigger = self.params.strip(self.stripchars).split(" ")[0]
            if trigger:
                self.trigger = trigger
            self.response = f"the current trigger is {self.trigger}"
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"
