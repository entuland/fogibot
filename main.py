import fogibot

import config

bot = fogibot.Bot(config)

bot.process_owner_message(f"join ##{config.nickname}")

bot.run()
