# @BotBot
A bot for [Euphoria](https://euphoria.io/) created by @myhandsaretypingwords that creates other bots.

## Installation

@BotBot uses Python 3. Make sure that you have `python3` and `pip3` installed.

### Linux
1. `pip3 install websocket-client`
2. `git clone https://github.com/ArkaneMoose/BotBot.git`
3. `cd BotBot`
4. `git submodule update --init`

To run @BotBot:

1. `./start_botbot.sh ROOMNAME` where `ROOMNAME` is the room at [Euphoria](https://euphoria.io/) where @BotBot will run.

To update @BotBot:

1. `git pull`
2. `git submodule update`

### Windows

On Windows, these commands should run in MinGW or Cygwin.

1. `pip3 install websocket-client`
2. `git clone https://github.com/ArkaneMoose/BotBot.git`
3. `cd BotBot`
4. `git submodule update --init`
5. `git update-index --assume-unchanged source/euphoria`
6. `rm source/euphoria`
7. `cp -r lib/EuPy/euphoria/ source/euphoria/`

To run @BotBot:

1. `./start_botbot.sh ROOMNAME` where `ROOMNAME` is the room at [Euphoria](https://euphoria.io/) where @BotBot will run.

To update @BotBot:

1. `git pull`
2. `git submodule update`
3. `rm -rf source/euphoria/`
4. `cp -r lib/EuPy/euphoria/ source/euphoria/`

## Help for @BotBot

### Usage
Create a bot with @BotName with some code.  
`!createbot @BotName CODE`

Same as the previous but specify the room to put the bot in.  
`!createbot &room @BotName CODE`

List all the bots that are currently running and have been created by @BotBot.  
`!list @BotBot`

Kill a bot with the name @BotName.  
`!kill @BotName`

Pause a bot with the name @BotName.  
`!pause @BotName`

Kill all the bots created by @BotBot.  
`!killall @BotName`

Take a snapshot of the state of @BotBot.  
`!save @BotBot`

Load the latest snapshot.  
`!load @BotBot latest`

Load a snapshot with a specific file name.  
`!load @BotBot FILENAME`

Restart @BotBot.  
`!restart @BotBot`

### Syntax
- `Regex -> Response`
- `Regex -> [List, of, responses, from, which, to, randomly, choose]`
- `Regex -> {Multiple, responses, to, a, single, message}`
- `Regex 1 -> Response 1; Regex 2 -> Response 2`

These response methods can also be nested:  
`Regex -> [a, {b, c}]`

Arguments can be left out. Simply use an empty string as the response, and no message will be displayed.  
This can be useful in lists; for example, `[Lorem ipsum,,,]` would display "Lorem ipsum" in response to the trigger only 1/4 of the time.

### Specials
Message sender
- `(sender)` to include the sender's name with spaces
- `(@sender)` to include an at-mention of the sender

### Spam
@BotBot has several anti-spam features to stop spammy bots that it creates.
- Bots may not interact with @BotBot.
- Bots may not send the `!ping` command.
- Bots may not `!restore`, `!pause`, or `!kill` other bots.
- Bots that are triggered more than 10 times in 5 seconds are automatically paused.

### Regexes
For those of you who don't know, "regex" stands for "regular expression", and is a way of doing pattern matching.  
You can find a good tutorial and reference [here](http://regular-expressions.info/).

### Good luck!
Good luck on your journey to becoming a bot programmer. 

There is always an instance of @BotBot up in [&bots](https://euphoria.io/room/bots/) for you to program. 

If you need help, you can ask @myhandsaretypingwords, @jedevc, or any of the other awesome Euphorians in [&programming](https://euphoria.io/room/programming/) for help with any bot-related questions. 

Have fun, and please be respectful! 
