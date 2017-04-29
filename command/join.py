from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        if self.owner == self.sender:
            if self.channel == self.botname:
                self.target = self.owner
            else:
                self.target = self.channel
            self.response = f"attempting to join {self.params}"
            self.raw_send = "JOIN :" + self.params
