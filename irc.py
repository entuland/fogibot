import asyncio
import re
from base64 import b64encode

# pattern taken from:
# https://mybuddymichael.com/writings/a-regular-expression-for-irc-messages.html
IRC_MSG_PATTERN = "^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$"

# class adapted from a sample kindly provided by https://github.com/emersonveenstra
class IRCClientProtocol(asyncio.Protocol):
    
    def __init__(self, conf, message_handler, logger):
        self._read_buffer = ""
        self._conf = conf
        self._log = logger
        self._message_handler = message_handler
        
    """ ========================================================================
        protocol required methods
    ======================================================================== """
        
    def connection_made(self, transport):
        self.transport = transport
        self.send_message("CAP REQ :sasl")
        self.send_message(f"NICK {self._conf.botname}")
        self.send_message(f"USER {self._conf.username} 8 * :{self._conf.realname}")

    def data_received(self, data):
        self._read_buffer += data.decode()
        messages = re.split("\r\n", self._read_buffer)
        # put back incomplete message, if any
        self._read_buffer = messages.pop()
        for msg in messages:        
            self.parse_message(msg)

    """ ========================================================================
        own methods
    ======================================================================== """

    def send_message(self, message, log_this = True):
        if log_this:
            self._log("--> " + message)
        self.transport.write(f"{message}\r\n".encode())

    #---------------------------------------------------------------------------
    # parse the message and process it directly in some cases
    # pass it over to the external _message_handler() in all other cases
    def parse_message(self, msg):
        match = re.search(IRC_MSG_PATTERN, msg)
        if not match:
            return
        
        sender = match.group(1)
        if sender:
            sender = sender.split("!")[0]
        irc_command = match.group(2)
        channel = match.group(3)
        message = match.group(4)

        if irc_command == "PING":
            self.send_message(f"PONG :{message}", log_this = False)
            # bail out immediately to avoid logging pings
            return

        self._log("<-- " + msg)

        if irc_command == "CAP":
            self.send_message("AUTHENTICATE PLAIN")
            
        elif irc_command == "AUTHENTICATE":
            authstring = b64encode(
                f"\0{self._conf.username}\0{self._conf.password}".encode()
            ).decode()
            self.send_message(f"AUTHENTICATE {authstring}", log_this = False)
        
        elif irc_command == "900":
            self.send_message("CAP END")
        
        elif irc_command == "376":
            for channel in self._conf.channels:
                self.send_message(f"JOIN {channel}")
        
        else:
            self._message_handler(sender, irc_command, channel, message)
