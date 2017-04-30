from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        if self.owner == self.sender:
            self.response = f"attempting to leave {self.params}"
            self.raw_send = "PART " + self.params
