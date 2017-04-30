Fogibot
=======
A python IRC bot

Features
--------

- extendable custom commands with dedicated files (see into the "command" 
    folder for examples)
- hotswapping of command source by disabling the caching system using the 
    "nocache" command - commands can be created and modified while the bot 
    is running
- dedicated file for matching any message against custom regexps
    (see "/command/matches.py")
- support for commands that only the owner can execute
- basic set of common commands (join, leave, quit)
- full guard against errors in any command (just keep an eye on the log for 
    a pointer about what went wrong when developing a command)
- automatic support for listing available commands and extracting their help 
    documentation from the intro doc string

Is it live somewhere?
---------------------

Yes, when I'm around, the bot can eventually be found on ##fogibot in the 
Freenode network, hopefully some good operator will let me run it in some more
crowded channel :)
