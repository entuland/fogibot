""" provides a set of triggers based on any content of the received messages """

import re

class Command():
    
    def run(self):
        pasteid = extract_pastebin_pasteid(self.params)
        
        if pasteid:
            self.response = (
                f"{self.sender}, please avoid using services with ads "
                "or obnoxious scripts, use one of these for sharing: "
                + self.sharing_bins
            )
            return
        
        if self.params.strip().lower() == "paste?":
            self.response = self.sharing_bins
            return
        
def extract_pastebin_pasteid(message):
    pattern = "[ph]astebin.com/((raw|dl|index|embed|report|print)/)?([\w\d\.]+)"
    match = re.search(pattern, message)
    if match:
        pasteid = match.group(3)
        if pasteid and len(pasteid):
            return pasteid
            