""" prints the status of the nocache flag or sets it to [params] ('on'/'off') """

class Command:
    
    owner_command = True
    
    def run(self):
        value = self.params.strip().lower()
        if value:
            self.nocache = value == "on"
        self.response = "nocache is " + ("on" if self.nocache else "off")
            