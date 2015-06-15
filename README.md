# @BotBot
A bot for [Euphoria](https://euphoria.io/) created by @myhandsaretypingwords that creates other bots.

## Usage
Create a bot with @BotName with some code.

    !createbot @BotName CODE
***
Same as the previous but specify the room to put the bot in.

    !createbot &room @BotName CODE
***
List all the bots that are currently running and have been created by this bot.

    !list @BotBot
***
Kill a bot with the name @BotName.

    !kill @BotName
***
Pause a bot with the name @BotName.

    !pause @BotName
***
Kill all the bots created by @BotBot.

    !killall @BotName
***
Take a snapshot of the state of @BotBot.

    !save @BotBot
***
Load the latest snapshot.

    !load @BotBot latest
Load a snapshot with a specific file name.

    !load @BotBot FILENAME
***
Restart @BotBot.

    !restart @BotBot

## Syntax
- Regex -> Response
- Regex -> [List, of, responses, from, which, to, randomly, choose]
- Regex -> {Multiple, responses, to, a, single, message}
- Regex 1 -> Response 1; Regex 2 -> Response 2

These can be nested:  
Regex -> {[a, {b, c}], d}

Arguments can be left out. Simply use an empty string as the response, and no message will be displayed.  
This can be useful in lists; for example, [Lorem ipsum,,,] would display "Lorem ipsum" in response to the trigger only 1/4 of the time.

## Specials
Responses can also use the username of the sender of the message that triggered the response.
Just use (sender) in the response to include the sender's name with spaces, and (@sender) to include an at-mention for the sender.

## Spam
@BotBot has several anti-spam features to stop spammy bots that it creates.
- Bots may not interact with @BotBot.
- Bots may not send the "!ping" command.
- Bots may not !restore, !pause, or !kill other bots.
- Bots that are triggered more than 10 times in 5 seconds are automatically paused.

##Regexes
For those of you who don't know, "regex" stands for "regular expression", and is a way of doing pattern matching.  
You can find a good tutorial and reference [here](http://regular-expressions.info/).

## Good luck!
Good luck on your journey to becoming a bot programmer. 

If you need help, you can ask @myhandsaretypingwords, @jedevc or any of the other awesome Euphorians in [&programming](https://euphoria.io/room/programming/) for help with any bot related questions.

Have fun, and please be respectful! 
