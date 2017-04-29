import fogibot

import config

bot = fogibot.Bot(config)

bot.process_command(config.owner, config.botname, "join", "##" + config.botname)

bot.run()
