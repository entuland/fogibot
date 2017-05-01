""" provides a set of triggers based on any content of the received messages """

import re


class Trigger:
    
    def __init__(self):
        self.trigger = ""
        self.description = ""
        self.response = ""
    
    def matches(self, message):
        if self.trigger:
            return message.strip().lower() == self.trigger + "?"


class Command:
    
    def __init__(self):
        self._triggers = []
        self._initialized = False
    
    def run(self):
        self.init()
        for trig in self._triggers:
            if trig.matches(self.params):
                self.response = trig.response
                return            

    # used by triggers.py to list available triggers
    def triggers_info(self):
        self.init()
        info = {}
        for trig in self._triggers:
            if trig.trigger and trig.description:
                info[trig.trigger] = trig.description
        return info
                
    # the properties of these Command() objects get set by fogibot.py
    # *after* that the object has been instantiated, for that reason
    # the following init() method can't be put in __init__()
    def init(self, data = None):
        if self._initialized:
            return
        self._initialized = True
        
        if not data:
            data = self
        
        # paste? trigger
        paste_trig = Trigger()
        paste_trig.trigger = "paste"
        paste_trig.description = "lists advised sharing bins"
        paste_trig.response = data.sharing_bins
        self._triggers.append(paste_trig)
    
        # pastebin regexp trigger    
        pastebin_trig = Trigger()
        pastebin_trig.matches = matches_pastebin_link
        pastebin_trig.response = [
            f"{data.sender}, please avoid using services with ads "
            "or obnoxious scripts, use one of these for sharing: "
        ] + data.sharing_bins
        self._triggers.append(pastebin_trig)


def matches_pastebin_link(message):
    pattern = "[ph]astebin.com/((raw|dl|index|embed|report|print)/)?([\w\d\.]+)"
    match = re.search(pattern, message)
    if match:
        pasteid = match.group(3)
        if pasteid and len(pasteid):
            return True
