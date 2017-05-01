""" list all the available triggers or details about a specific [params] trigger """

from command.matches import Command as Matches

class Command:
        
    def run(self):
        trigger = self.params.strip(self.strip_chars).lower()
        
        matches = Matches()
        
        # proxies self as data to the matches.py Command() class
        # to avoid hitting a default empty object
        matches.init(data = self)
        
        info = matches.triggers_info()
        
        if trigger in info:
            self.response = f"'{trigger}?' " + info[trigger]
            return
        
        self.response = "available triggers: "
        self.response += "? ".join(info.keys()) + "?"
