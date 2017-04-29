import re
import requests
import time

import logger
import irc
import utils

class Bot:
    
    def __init__(self, conf):
        self._conf = conf
        self._log = logger.Logger(conf.username + " " + time.strftime("%Y-%m-%d"))
        self._log.level = self._log.ALL
        self._log.echo = True
        self._irc = irc.Connection(conf.host, conf.port, self._log)
        self._irc.user(conf.username, conf.password, conf.realname)
        self._irc.nick(conf.nickname)

    def run(self):
        while True:
            for line in self._irc.get_lines():
                name = channel = message = ""
                if line.find("PING :") == 0:
                    self._irc.pong(line.split(":", 1)[1].strip())
                else:
                    self._log(line)
                if line.find("PRIVMSG") != -1:
                    name = line.split('!',1)[0][1:]
                    parts = line.split('PRIVMSG',1)[1].split(':',1)
                    channel = parts[0].strip()
                    message = parts[1].strip()
                    self._process_message(name, channel, message)

    """ ========================================================================
        message processing
    ======================================================================== """

    def process_owner_message(self, message):
        tokens, count = utils.tokenize(message)
        if not count:
            return
        command = tokens[0]
        if command == "quit":
            self._irc.send_message(self._conf.owner, f"quitting, {self._conf.owner}!")
            self._irc.quit(f"{self._conf.nickname} heads back to the workshop")
            exit(0)

        if command == "join" and count > 1:
            channel = tokens[1]
            self._irc.send_message(self._conf.owner, f"attempting to join {channel}")
            self._irc.join_channel(channel)

    def _process_message(self, name, channel, message):
        if name == self._conf.owner and channel == self._conf.nickname:
            self._process_owner_message(message)
        elif channel != self._conf.nickname:
            self._process_channel_message(name, channel, message)

    def _process_channel_message(self, name, channel, message):
        pasteid = self._extract_pastebin_pasteid(message)
        tokens, count = utils.tokenize(message)
        if count and tokens[0] == self._conf.nickname:
            self._process_bot_command(name, channel, tokens[1:])
        elif pasteid:
            self._pastebin_nag_message(name, channel)
            
    """ ========================================================================
        bot commands
    ======================================================================== """

    def _process_bot_command(self, name, channel, tokens):
        command = ""
        if len(tokens):
            command = tokens[0]
        self._bot_command(command)(name, channel, tokens[1:])
        
    def _bot_command(self, command):
        return {
            "none":     self._bot_command_none,
            "help":     self._bot_command_help,
            "share":    self._bot_command_share,
            "repaste":  self._bot_command_repaste,
        }.get(command,  self._bot_command_none)


    def _bot_command_none(self, name, channel, tokens):
        self._irc.send_message(channel, f"{name}, type '{self._conf.nickname} help' for available commands")
        
    def _bot_command_help(self, name, channel, tokens):
        self._irc.send_message(channel, f"'{self._conf.nickname} repaste <link>' repastes <link> to {bin_service} (only pastebin.com supported); '{self._conf.nickname} share' prints suggestions about sharing services")

    def _bot_command_repaste(self, name, channel, tokens):
        if len(tokens):
            pasteid = self._extract_pastebin_pasteid(tokens[0])
            if pasteid:
                self._scrape_pastebin(name, channel, pasteid)
                return
        self._irc.send_message(channel, f"{name}, missing recognizable pastebin.com link from 'repaste' command")

    def _bot_command_share(self, name, channel, tokens):
        self._irc.send_message(channel, "Suggested sharing services: gist.github.com (multiple files support), ideone.com (runnable code), jsfiddle.net (HTML+CSS+JS showcase), pasteconf.net (conf files), postimage.io (family safe images)")

    """ ========================================================================
        pastebin handling
    ======================================================================== """

    def _get_url(self, url):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r.text
        except:
            pass
        self._log.error(f"Unable to get [{url}]")

    def _extract_pastebin_pasteid(self, message):
        pattern = "pastebin.com/((raw|dl|index|embed|report|print)/)?([\w\d]+)"
        match = re.search(pattern, message)
        if match:
            pasteid = match.group(3)
            if pasteid and len(pasteid):
                return pasteid

    def _get_alternative_link(self, text):
        bin_service = "https://cpy.pt"
        try:
            r = requests.post(bin_service, data = {"paste": text, "raw": "false"})
            if r.status_code == 200:
                return r.text.split("|", 1)[0].strip()
        except:
            pass
        self._log.error(f"Unable to post to [{bin_service}]")

    def _scrape_pastebin(self, name, channel, pasteid):
        pastebin_link = "https://pastebin.com/raw/" + pasteid
        text = self._get_url(pastebin_link)
        if text:
            link = self._get_alternative_link(text)
            if link:
                response = f"Repasting for {name}: {link} <-- this temporary link will expire in one hour"
            else:
                response = f"Sorry {name}, I'm unable to get a link from {bin_service} right now"
        else:
            response = f"Sorry {name}, I'm unable to access {pastebin_link} right now"
        self._irc.send_message(channel, response)
            
    def _pastebin_nag_message(self, name, channel):
        self._irc.send_message(channel, f"{name}, please avoid pastebin.com links! type '{self._conf.nickname} help' for other bins or scraping commands")

