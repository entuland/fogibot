"""
    changes the bot's trigger to [params] (alphanumeric chars only)
"""

class Command:
    
    owner_command = True
    
    def run(self):
        trigger = self.params.strip(self.strip_chars).split(" ")[0]
        if trigger:
            self.trigger = trigger
        self.response = f"the current trigger is {self.trigger}"
