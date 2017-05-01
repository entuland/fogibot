""" prints the status of the nocache flag or sets it to [params] ('on'/'off') """

class Command():
    
    def run(self):
        if self.owner == self.sender:
            value = self.params.strip().lower()
            if value:
                self.nocache = value == "on"
            self.response = "nocache is " + ("on" if self.nocache else "off")
        else:
            self.response = f"{self.sender}, sorry, only {self.owner} can execute this command"            