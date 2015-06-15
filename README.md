# @BotBot
A meta-bot for [Euphoria](https://euphoria.io/)

## Help text
You can view this help text by sending "!help @BotBot" in a room in which @BotBot is present.

@BotBot: MAKING BOT CREATION EASY
@BotBot is a bot created by @myhandsaretypingwords that creates other bots.

How to use:
!createbot @BotName code
!createbot &room @BotName code

The syntax is simple:
Regex -> Response
Regex -> [List, of, responses, from, which, to, randomly, choose]
Regex -> {Multiple, responses, to, a, single, message}
Regex 1 -> Response 1; Regex 2 -> Response 2

These can be nested:
Regex -> {[a, {b, c}], d}

Responses can be no-ops. Simply use an empty string as the response, and no message will be displayed.
This can be useful in lists; for example, [Lorem ipsum,,,] would display "Lorem ipsum" in response to the trigger only 1/4 of the time.

Responses can also use the username of the sender of the message that triggered the response.
Just use (sender) in the response to include the sender's name with spaces, and (@sender) to include an at-mention for the sender.

For those of you who don't know, "regex" stands for "regular expression", and is a way of doing pattern matching.
You can find a good tutorial and reference at regular-expressions.info. (@myhandsaretypingwords is not affiliated with regular-expressions.info/.)
Of course, you can ask @myhandsaretypingwords or the Euphorians in &programming for help with regexes.

@BotBot has several anti-spam features to stop spammy bots that it creates.
- Bots may not interact with @BotBot.
- Bots may not send the "!ping" command.
- Bots may not !restore, !pause, or !kill other bots.
- Bots that are triggered more than 5 times in 3 seconds are automatically paused.

Have fun, and please be respectful!

To see all bots created by this bot that are currently running, type "!list @BotBot".
To pause a bot created by this bot, type "!pause @BotName".
To kill a bot created by this bot, type "!kill @BotName".
To kill ALL bots created by this bot, type "!killall @BotBot".

To take a snapshot of @BotBot's current state, type "!save @BotBot".
Snapshots can be loaded again later by typing "!load @BotBot" followed by either the word "latest" or the snapshot filename, which is provided at the time the snapshot is taken.

To restart @BotBot, type "!restart @BotBot".
