import asyncio
import os
import re
import time
from importlib import import_module, reload

import irc
import logger
import utils

STRIP_CHARS = ".:,;<>\"'!?"

class Bot:
    
    def __init__(self, conf):
        self._conf = conf
        self._basepath = os.path.dirname(os.path.realpath(__file__))

        self._log = logger.Logger(conf.username + " " + time.strftime("%Y-%m-%d"))
        self._log.level = self._log.ALL
        self._log.echo = True

        self._nocache = False
        self._pending = []

        self._irc = irc.IRCClientProtocol(self._conf, self._message_handler, self._log)

    # --------------------------------------------------------------------------
    # prepare and start the asyncio loop
    def run(self):
        self._loop = asyncio.get_event_loop()
        conn = self._loop.create_connection(
            lambda: self._irc, self._conf.host, self._conf.port, ssl = True
        )
        self._loop.run_until_complete(conn)
        self._loop.run_forever()
        self._loop.close()
        
    """ ========================================================================
        network interaction
    ======================================================================== """
    
    # --------------------------------------------------------------------------
    # send a PRIVMS
    def _send_message(self, target, message):
        self._raw_send(f"PRIVMSG {target} :{message}")
    
    # --------------------------------------------------------------------------
    # send data out to the network
    def _raw_send(self, message):
        self._irc.send_message(message)
    
    # --------------------------------------------------------------------------
    # handler called by the IRCClientProtocol object in the asyncio loop
    def _message_handler(self, sender, irc_command, channel, message):
        if False:
            self._log({
                "self": self,
                "sender": sender,
                "irc_command": irc_command,
                "channel": channel,
                "message": message,
            })

        if irc_command == "PRIVMSG":
            self._process_line(sender, channel, message)
        
        if irc_command == "433":
            self._new_nick()
        
    """ ========================================================================
        message processing
    ======================================================================== """

    # --------------------------------------------------------------------------
    # check if a command exists otherwise pass the call to the matchers
    def _process_line(self, sender, channel, message):
        if self._process_trigger_command(sender, channel, message):
            return
        self._process_command(sender, channel, "matches", message, quiet = True)
    
    # --------------------------------------------------------------------------
    # verify if the message starts with the botname or its trigger
    # and some params have been appended to it, return False otherwise
    def _process_trigger_command(self, sender, channel, message):
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
        
        self._process_command(sender, channel, command, params)
        return True
        
    # --------------------------------------------------------------------------
    # attempt a new nick if the current one is in use
    def _new_nick(self):
        self._conf.botname += "_"
        self._conf.trigger += "_"
        self._raw_send(f"NICK {self._conf.botname}")
    
    """ ========================================================================
        command processing
    ======================================================================== """

    # --------------------------------------------------------------------------
    # verify if the provided command is a valid one and load/execute it
    # catch any error that may arise while loading or executing it
    def _process_command(self, sender, channel, command, params, quiet = False):
        filename = self._basepath + f"/command/{command}.py"
        target = channel
        if channel == self._conf.botname:
            target = sender

        if quiet:
            target = self._conf.owner
        
        if os.path.isfile(filename):
            try:
                self._execute_command(command, sender, channel, params)
            except BaseException as error:
                self._send_message(
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
                self._log.error(error.__traceback__)
                
        else:
            self._send_message(target, f"{sender}, type '{self._conf.trigger} help'")
    
    # --------------------------------------------------------------------------
    # at this stage, the command has been confirmed as valid and can be executed
    def _execute_command(self, command, sender, channel, params):
        module = import_module("command." + command)
        if(self._nocache):
            reload(module)
        
        com = module.Command()

        # bail out if the command failed to implement run()
        if not callable(getattr(com, "run", None)):
            return
        
        # inject all the variables the command can access or alter
        com.quit = False
        com.response = ""
        com.raw_messages = ""
        
        com.sender = sender
        com.owner = self._conf.owner
        
        com.botname = self._conf.botname
        com.channel = channel
        com.params = params
        com.trigger = self._conf.trigger
        com.nocache = self._nocache
        com.strip_chars = STRIP_CHARS
        com.sharing_bins = self._conf.sharing_bins
        com._log = self._log
        
        # preset the target depending on where the command has been received
        com.target = com.channel
        if com.channel == com.botname:
            com.target = com.sender
        
        # verify and bail out from execution if lacking owner privileges
        owner_command = getattr(com, "owner_command", False)
        com.is_owner = (com.owner == com.sender)
        if not com.is_owner and owner_command:
            self._send_message(
                com.target, 
                f"{com.sender}, sorry, only {com.owner} can execute this command"
            )
            return

        # execute the command
        com.run()
        
        # apply changes to some variables performed by the command
        self._conf.trigger = com.trigger
        self._nocache = com.nocache
        
        # send out responses
        if com.target and com.response:
            if not isinstance(com.response, list):
                com.response = [com.response]
            for response in com.response:
                self._send_message(com.target, response)
        
        
        # send out raw messages
        if com.raw_messages:
            if not isinstance(com.raw_messages, list):
                com.raw_messages = [com.raw_messages]
            for raw_message in com.raw_messages:
                self._raw_send(raw_message)
        
        # stop the asyncio loop if requested
        if com.quit:
            self._loop.stop()
