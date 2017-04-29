from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        if self.owner == self.sender:
            value = self.params.strip().lower()
            if value:
                self.livereload = value == "on"
            self.response = "livereload is " + ("on" if self.livereload else "off")
            