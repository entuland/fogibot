"""
    DO NOT ALTER THIS FILE!
"""

class BaseCommand:
    def __init__(self):        
        self.quit = False
        self.botname = "botname"
        self.owner = "owner"
        self.sender = "sender"
        self.channel = ""
        self.params = ""
        self.target = ""
        self.trigger = "trigger"
        self.response = ""
        self.raw_send = ""
        self.nocache = False
        
    def init(self):
        pass
        