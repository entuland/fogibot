""" list available commands or specific help about the [params] command"""
import os
from importlib import import_module, reload
import re

from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def init(self):
        self._basepath = os.path.dirname(os.path.realpath(__file__))
    
    def run(self):
        files = os.listdir(self._basepath)
        commands = []
        for file in files:
            filename = self._basepath + "/" + file
            if (not os.path.isfile(filename) 
                    or file[-3:] != ".py" 
                    or file == "basecommand.py"):
                continue
            commands.append(file[0:-3])
        commands.sort()
        subcommand = self.params.split(" ")[0].lower()
        if subcommand in commands:
            self.help(subcommand)
        else:
            self.response = "available commands: " \
                + " ".join(commands) \
                + f" | type '{self.trigger} help <command>' for detailed help"
    
    def help(self, command):
        module = import_module("command." + command)
        if(self.livereload):
            reload(module)
        doc = module.__doc__
        if not doc:
            self.response = f"sorry, no help info for command '{command}'"
            return
        doc = re.sub(r"[\r\n\t ]+", " ", module.__doc__).strip()
        self.response = f"'{self.trigger} {command} [params]' " + doc
        