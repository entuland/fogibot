import os
import sys
import re
import requests
import time
import traceback
from importlib import import_module, reload

import irc
import logger
import utils

STRIP_CHARS = ".:,;<>\"'!?"

# pattern taken from:
# https://mybuddymichael.com/writings/a-regular-expression-for-irc-messages.html
IRC_MSG_PATTERN = "^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$"

class Bot:
    
    def __init__(self, conf):
        self._conf = conf
        self._basepath = os.path.dirname(os.path.realpath(__file__))

        self._log = logger.Logger(conf.username + " " + time.strftime("%Y-%m-%d"))
        self._log.level = self._log.ALL
        self._log.echo = True

        self._running = True
        self._nocache = False
        self._pending = []

        self._irc = irc.Connection(conf.host, conf.port, self._log)
        self._irc.nick(conf.botname)
        self._irc.user(conf.username, conf.password, conf.realname)

    def run(self):
        while self._running:
            for line in self._irc.get_lines():
                match = re.search(IRC_MSG_PATTERN, line)
                if not match:
                    continue
                    
                sender = match.group(1)
                if sender:
                    sender = sender.split("!")[0]
                irc_command = match.group(2)
                channel = match.group(3)
                message = match.group(4)
                
                if irc_command == "PING":
                    self._irc.pong(message)
                    continue
                    
                self._log(line)
                
                if irc_command == "PRIVMSG":
                    self._process_line(sender, channel, message)
                
                if irc_command == "433":
                    self._new_nick()
                
                if irc_command == "001":
                    for func in self._pending:
                        func()
        
    def _process_line(self, sender, channel, message):
        if self._attempt_command(sender, channel, message):
            return
        self.process_command(sender, channel, "matches", message, quiet = True)
        

    def _attempt_command(self, sender, channel, message):
        parts = message.split(" ", 2)
        parts = list(map(str.strip, parts))
        parts = list(filter(None, parts))
        
        if len(parts) < 2:
            return False
        
        trigger = parts[0].lower().strip(STRIP_CHARS)
        if trigger != self._conf.trigger and trigger != self._conf.botname:
            return False
        
        command = parts[1].lower().strip(STRIP_CHARS)
        params = ""
        if len(parts) > 2:
            params = parts[2]
        
        self.process_command(sender, channel, command, params)
        return True
        
        
    def _new_nick(self):
        self._conf.botname += "_"
        self._conf.trigger += "_"
        self._irc.nick(self._conf.botname)
            
    def join(self, channel):
        self._pending.append(lambda: 
            self.process_command(
                self._conf.owner, 
                self._conf.botname, 
                "join",
                channel
            )
        )
    
    """ ========================================================================
        message processing
    ======================================================================== """

    def process_command(self, sender, channel, command, params, quiet = False):
        filename = self._basepath + f"/command/{command}.py"
        target = channel
        if channel == self._conf.botname:
            target = sender

        if quiet:
            target = self._conf.owner
        
        if command != "basecommand" and os.path.isfile(filename):
            try:
                self._execute_command(command, sender, channel, params)
            except BaseException as error:
                self._irc.send_message(
                    target, 
                    f"{sender}, sorry, unable to execute '{command}'"
                )
                self._log.error(
                    f"Unable to execute command: {command} " 
                    f"sender: {sender} " 
                    f"channel: {channel} " 
                    f"params: {params} " 
                )
                self._log.error(error)
                
        else:
            self._irc.send_message(target, f"{sender}, type '{self._conf.trigger} help'")
            
    def _execute_command(self, command, sender, channel, params):
        module = import_module("command." + command)
        if(self._nocache):
            reload(module)
        
        com = module.Command()
        com.init()
        
        com.owner = self._conf.owner
        com.botname = self._conf.botname
        com.sender = sender
        com.channel = channel
        com.params = params
        com.trigger = self._conf.trigger
        com.nocache = self._nocache
        com.stripchars = STRIP_CHARS
        com.sharing_bins = self._conf.sharing_bins
        
        com.target = com.channel
        if com.channel == com.botname:
            com.target = com.sender
        
        com.run()
        
        self._conf.trigger = com.trigger
        self._nocache = com.nocache
        
        if com.target and com.response:
            self._irc.send_message(com.target, com.response)
        
        if com.raw_send:
            self._irc.raw_send(com.raw_send)
        
        if com.quit:
            self._running = False
