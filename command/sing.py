""" well... just try it """
import os

from command.basecommand import BaseCommand

class Command(BaseCommand):
    
    def run(self):
        self.response = f"{self.sender}, no, you don't really want that..."
        