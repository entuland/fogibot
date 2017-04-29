import fogibot

import config

import sys

print("sys.stdout.encoding", sys.stdout.encoding)
print("sys.getdefaultencoding()", sys.getdefaultencoding())
print("sys.getfilesystemencoding()", sys.getfilesystemencoding())

bot = fogibot.Bot(config)

bot.process_command(config.owner, config.botname, "join", "##" + config.botname)

bot.run()
