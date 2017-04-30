""" prints the status of the livereload flag or sets it to [params] ('on'/'off') """
from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        if self.owner == self.sender:
            value = self.params.strip().lower()
            if value:
                self.livereload = value == "on"
            self.response = "livereload is " + ("on" if self.livereload else "off")
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"            