from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        if self.owner == self.sender:
            self.quit = True
            self.raw_send = "QUIT :" + self.params
