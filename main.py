import fogibot

import config

bot = fogibot.Bot(config)

bot.join("##" + config.botname)

bot.run()
