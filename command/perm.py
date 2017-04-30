""" computes some data about permutations of the [params] string """

from command.basecommand import BaseCommand

class Command(BaseCommand):
        
    def run(self):
        s = self.params.strip()
        if len(s) < 2 or len(s) > 8:
            self.response = f"{self.sender}, the length of the provided string must be from 2 to 8"
            return
            
        first = firstPermutation(s)
        pos, tot = findPosition(s)        
        self.response = f"{self.sender}, String: {s}, Position: {pos+1}, Rev. Position: {tot-pos}, Total Permutations: {tot}"

def findPosition(s):
    i = 0
    pos = -1
    f = firstPermutation(s)
    while f != False:
        if f == s:
            pos = i
        f = nextPermutation(f)
        i += 1
    return pos, i # i = total permutations
    
def firstPermutation(s):
    return "".join(sorted(s))
    
def nextPermutation(s):
    s = list(s)
    length = len(s)

    if not length:
        return false
        
    k = length - 2
    while k >= 0 and s[k] >= s[k+1]:
        k -= 1
    
    if k < 0:
        return False
    
    j = length - 1
    while s[k] >= s[j]:
        j -= 1
        
    s[k], s[j] = s[j], s[k]
        
    return "".join(s[:k+1] + s[k+1:][::-1])