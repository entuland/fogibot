""" list available commands or specific help about the [params] command"""
import os
from importlib import import_module, reload
import re

class Command:
    
    def run(self):
        basepath = os.path.dirname(os.path.realpath(__file__))
        files = os.listdir(basepath)
        commands = {}
        names = []
        for file in files:
            filename = basepath + "/" + file
            if (not os.path.isfile(filename) 
                    or file[-3:] != ".py"
                    or file == "matches.py"):
                continue
            name = file[0:-3]
            commands[name] = self.load_command(name)
            names.append(name)
        names.sort()
        about = self.params.split(" ")[0].lower()
        if about in commands:
            self.help(commands[about], about)
            return
        
        parts = ["available commands:"]
        for name in names:
            com = commands[name]
            owner_command = getattr(com, "owner_command", False)
            if self.is_owner and owner_command:
                parts.append(name + "*")
            elif not owner_command:
                parts.append(name)  
    
        self.response = (
            " ".join(parts)
            + (f" | * = owner command" if self.is_owner else "")
            + f" | type '{self.trigger} help <command>' for detailed help"
        )
        
    def load_command(self, name):
        module = import_module("command." + name)
        if(self.nocache):
            reload(module)
        com = module.Command()
        com._doc = module.__doc__
        return com 
    
    def help(self, com, name):
        if not com._doc:
            self.response = f"sorry, no help info for command '{name}'"
            return
        doc = re.sub(r"[\r\n\t ]+", " ", com._doc).strip()
        self.response = f"'{self.trigger} {name} [params]' " + doc
