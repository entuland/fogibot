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

class Bot:
    
    def __init__(self, conf):
        self._conf = conf
        self._running = True
        self._log = logger.Logger(conf.username + " " + time.strftime("%Y-%m-%d"))
        self._log.level = self._log.ALL
        self._log.echo = True
        self._irc = irc.Connection(conf.host, conf.port, self._log)
        self._irc.user(conf.username, conf.password, conf.realname)
        self._irc.nick(conf.botname)
        self._basepath = os.path.dirname(os.path.realpath(__file__))
        self._livereload = False

    def run(self):
        while self._running:
            for line in self._irc.get_lines():
                if line.find("PING :") == 0:
                    self._irc.pong(line.split(":", 1)[1].strip())
                    continue
                self._log(line)
                if line.find("PRIVMSG") != -1:
                    self._process_line(line)
        for x in range(3, 0, -1):
            print(f"Closing in {x}", flush = True)
            time.sleep(1)
        
    def _process_line(self, line):
        sender = line.split('!',1)[0][1:]
        parts = line.split('PRIVMSG',1)[1].split(':',1)
        channel = parts[0].strip()
        message = parts[1].strip()
        
        parts = message.split(" ", 2)
        parts = list(map(str.strip, parts))
        parts = list(filter(None, parts))
        
        if len(parts) < 2:
            return
        
        trigger = parts[0].lower().strip(STRIP_CHARS)
        if trigger != self._conf.trigger:
            return
        
        command = parts[1].lower().strip(STRIP_CHARS)
        params = ""
        if len(parts) > 2:
            params = parts[2]
        
        self.process_command(sender, channel, command, params)

    """ ========================================================================
        message processing
    ======================================================================== """

    def process_command(self, sender, channel, command, params):
        filename = self._basepath + f"/command/{command}.py"
        target = channel
        if channel == self._conf.botname:
            target = sender

        if command != "basecommand" and os.path.isfile(filename):
            try:
                self._execute_command(command, sender, channel, params)
            except BaseException as error:
                self._irc.send_message(
                    target, 
                    f"{sender}, sorry, unable to execute '{command}'"
                )
                self._log.error(
                    "Unable to execute command: {command} " 
                    "sender: {sender} " 
                    "channel: {channel} " 
                    "params: {params} " 
                )
                self._log.error(error)
                
        else:
            self._irc.send_message(target, f"{sender}, type '{self._conf.botname} help'")
            
    def _execute_command(self, command, sender, channel, params):
        module = import_module("command." + command)
        if(self._livereload):
            reload(module)
        
        com = module.Command()
        
        com.owner = self._conf.owner
        com.botname = self._conf.botname
        com.sender = sender
        com.channel = channel
        com.params = params
        com.livereload = self._livereload
        
        com.target = com.channel
        if com.channel == com.botname:
            com.target = com.sender
        
        com.run()
        
        self._livereload = com.livereload
        
        if com.target and com.response:
            self._irc.send_message(com.target, com.response)
        
        if com.raw_send:
            self._irc.raw_send(com.raw_send)
        
        if com.quit:
            self._running = False
