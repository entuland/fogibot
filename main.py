import fogibot

import config

import sys

bot = fogibot.Bot(config)

bot.join("##" + config.botname)

bot.run()
