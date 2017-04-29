import os

from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        basepath = os.path.dirname(os.path.realpath(__file__))
        files = os.listdir(basepath)
        commands = []
        for file in files:
            filename = basepath + "/" + file
            if (not os.path.isfile(filename) 
                    or file[-3:] != ".py" 
                    or file == "basecommand.py"
                    or file == "help.py"):
                continue
            commands.append(file[0:-3])
        commands.sort()
        self.response = "available commands: " + " ".join(commands)
        