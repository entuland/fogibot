import logging
import re
import requests
import socket

# ================================================================================
# initial setup
# ================================================================================

host = "chat.freenode.net"
port = 6667

import config
botname = config.botname
ident = config.ident
realname = config.realname
owner = config.owner
password = config.password

bin_service = "https://cpy.pt"

s = socket.socket()

# ================================================================================
# logging setup
# ================================================================================

logger = logging.getLogger(botname)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_file_handler = logging.FileHandler(botname + ".log")
log_file_handler.setLevel(logging.DEBUG)
log_file_handler.setFormatter(formatter)

log_console_handler = logging.StreamHandler()
log_console_handler.setLevel(logging.DEBUG)

logger.addHandler(log_file_handler)
logger.addHandler(log_console_handler)

def log(msg):
    logger.info(msg)

# ================================================================================
# server functions
# ================================================================================

def connect():
    s.connect((host, port))
    raw_send(f"USER {ident} {host} {password} :{realname} \r\n", False)
    raw_send(f"NICK {botname} \r\n")

def get_chunk():
    return s.recv(2048).decode("UTF-8")

def raw_send(msg, log_this = True):
    if log_this:
        log(f"SENT: {msg}")
    s.send(bytes(msg, "UTF-8"))

def send_message(target, message):
    raw_send(f"PRIVMSG {target} :{message}\r\n")

def join_channel(channel):
    send_message(owner, f"attempting to join {channel}")
    raw_send(f"JOIN {channel}\r\n")

def pong(name):
    raw_send(f"PONG :{name}\r\n", False)

# ================================================================================
# message processing helpers
# ================================================================================

def tokenize(message):
    parts = message.split()
    tokens = []
    for part in parts:
        token = part.strip(" .,:;!?'\"")
        if token:
            tokens.append(token)
    return tokens, len(tokens)

# ================================================================================
# message processing
# ================================================================================

def process_message(name, channel, message):
    if name == owner and channel == botname:
        process_owner_message(message)
    elif channel != botname:
        process_channel_message(name, channel, message)

def process_owner_message(message):
    tokens, count = tokenize(message)
    if not count:
        return
    command = tokens[0]
    if command == "quit":
        send_message(owner, f"quitting, {owner}!")
        raw_send(f"QUIT :{botname} heads back to the workshop\r\n")
        exit(0)

    if command == "join" and count > 1:
        join_channel(tokens[1])

def process_channel_message(name, channel, message):
    pasteid = extract_pastebin_pasteid(message)
    tokens, count = tokenize(message)
    if count and tokens[0] == botname:
        process_bot_command(name, channel, tokens[1:])
    elif pasteid:
        pastebin_nag_message(name, channel)
        
# ================================================================================
# bot commands
# ================================================================================

def process_bot_command(name, channel, tokens):
    command = ""
    if len(tokens):
        command = tokens[0]
    bot_command(command)(name, channel, tokens[1:])
    
def bot_command(command):
    return {
        "none":     bot_command_none,
        "help":     bot_command_help,
        "share":    bot_command_share,
        "repaste":  bot_command_repaste,
    }.get(command,  bot_command_none)


def bot_command_none(name, channel, tokens):
    send_message(channel, f"{name}, type '{botname} help' for available commands")
    
def bot_command_help(name, channel, tokens):
    send_message(channel, f"'{botname} repaste <link>' repastes <link> to {bin_service} (only pastebin.com supported); '{botname} share' prints suggestions about sharing services")

def bot_command_repaste(name, channel, tokens):
    if len(tokens):
        log(tokens)
        pasteid = extract_pastebin_pasteid(tokens[0])
        log(pasteid)
        if pasteid:
            scrape_pastebin(name, channel, pasteid)
            return
    send_message(channel, f"{name}, missing recognizable pastebin.com link from 'repaste' command")

def bot_command_share(name, channel, tokens):
    send_message(channel, "Suggested sharing services: gist.github.com (multiple files support), ideone.com (runnable code), jsfiddle.net (HTML+CSS+JS showcase), pasteconf.net (conf files), postimage.io (family safe images)")

# ================================================================================
# pastebin handling
# ================================================================================

def get_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
    except:
        pass
    log(r.headers)

def extract_pastebin_pasteid(message):
    pattern = "pastebin.com/((raw|dl|index|embed|report|print)/)?([\w\d]+)"
    match = re.search(pattern, message)
    if match:
        pasteid = match.group(3)
        if pasteid and len(pasteid):
            return pasteid

def get_alternative_link(text):
    try:
        r = requests.post(bin_service, data = {"paste": text, "raw": "false"})
        if r.status_code == 200:
            return r.text.split("|", 1)[0].strip()
    except:
        pass
    log(r.headers)

def scrape_pastebin(name, channel, pasteid):
    pastebin_link = "https://pastebin.com/raw/" + pasteid
    text = get_url(pastebin_link)
    if text:
        link = get_alternative_link(text)
        if link:
            response = f"Repasting for {name}: {link} <-- this temporary link will expire in one hour"
        else:
            response = f"Sorry {name}, I'm unable to get a link from {bin_service} right now"
    else:
        response = f"Sorry {name}, I'm unable to access {pastebin_link} right now"
    send_message(channel, response)
        
def pastebin_nag_message(name, channel):
    send_message(channel, f"{name}, please avoid pastebin.com links! type '{botname} help' for other bins or scraping commands")
    
# ================================================================================
# main loop
# ================================================================================

def main_loop():
    while 1:
        ircmsg = get_chunk().strip('\r\n')

        name = channel = message = ""
        
        if ircmsg.find("PING :") == 0:
            pong(ircmsg.split(":", 1)[1].strip())
        else:
            log(ircmsg)
        if ircmsg.find("PRIVMSG") != -1:
            name = ircmsg.split('!',1)[0][1:]
            parts = ircmsg.split('PRIVMSG',1)[1].split(':',1)
            channel = parts[0].strip()
            message = parts[1].strip()
            process_message(name, channel, message)

# ================================================================================
# program start
# ================================================================================

connect()
join_channel(f"##{botname}")
main_loop()
