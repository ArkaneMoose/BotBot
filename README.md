# @BotBot

[![Build Status](https://travis-ci.org/ArkaneMoose/BotBot.svg?branch=tests)](https://travis-ci.org/ArkaneMoose/BotBot)

A bot for [Euphoria](https://euphoria.io/) created by @myhandsaretypingwords that creates other bots.

## Installation

@BotBot uses Python 3.

To install: `python3 setup.py install`

To run: `botbot`

## Configuration

### Command-line options

The easiest way to make one-time configuration changes is through the command-line options.  

The command-line options are:

Short form        | Long form                     | Description                                        | Default value
------------------|-------------------------------|----------------------------------------------------|---------------------------------------------
`-h`              | `--help`                      | Show a help message and exit                       |  
`-r ROOM`         | `--room ROOM`                 | Room in Euphoria where @BotBot should reside       | [`testing`](https://euphoria.io/room/testing/)
`-p PASSWORD`     | `--password PASSWORD`         | Password for room if necessary                     | None
`-n NICKNAME`     | `--nickname NICKNAME`         | Custom nickname for @BotBot                        | `BotBot`
`-s SNAPSHOT_DIR` | `--snapshot-dir SNAPSHOT_DIR` | Directory where snapshots will be read and written | None

These are also all described in @BotBot's help text, which you can view using `botbot --help`.

### Configuration file

You can also create a JSON file containing your custom configuration.

Default configuration values are in `defaults.json`. If a setting is not specified in your configuration file, it
defaults to the value shown in `defaults.json`.

The configuration file is specified as the first positional argument, as in `botbot /path/to/config.json`.

The possible options that can be specified in the configuration file are as follows:

JSON key              | Description                                                            | Default value
----------------------|------------------------------------------------------------------------|---------------------------------------------
`"room"`              | Room in Euphoria where @BotBot should reside                           | [`"testing"`](https://euphoria.io/room/testing/)
`"password"`          | Password for room if necessary                                         | `null`
`"nickname"`          | Custom nickname for @BotBot                                            | `"BotBot"`
`"helpText"`          | Custom help text for @BotBot; shown when someone sends `!help @BotBot` | See [`defaults.json`](https://github.com/ArkaneMoose/BotBot/blob/master/defaults.json#L5).
`"shortHelpText"`     | Custom short help text for @BotBot; shown when someone sends `!help`   | See [`defaults.json`](https://github.com/ArkaneMoose/BotBot/blob/master/defaults.json#L6).
`"snapshotDirectory"` | Directory where snapshots will be read and written                     | `null`


### Precedence

Command-line options take precedence over the configuration file, which takes precedence over the default settings.

For any given configurable setting:
- If there is a command-line option specifying that setting, that value is used.
- Otherwise, if there is a value in the specified configuration file, that value is used.
- Otherwise, the default value is used.

### Ignored files and directories

For your convenience, certain files may be placed right inside the repository without interfering
with git. These files have been added to the `.gitignore` file.

- `config.json`  
  This file is intended to be your own custom configuration file. It should be located in the root
  of the repository for it to be ignored by git.
- `snapshots/`  
  A `snapshots` directory is included in the repository, which contains a single file, `snapshots.txt`.
  Any other file inside the directory should be ignored by git. Therefore, this directory is a good
  place to use as a snapshot directory.

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

### More info
View the [@BotBot wiki](https://github.com/ArkaneMoose/BotBot/wiki) for a comprehensive guide on how to use @BotBot, including a guide on how to write @BotBot code and a list of features and restrictions that bots created with @BotBot have.

### Good luck!
Good luck on your journey to becoming a bot programmer.

There is always an instance of @BotBot up in [&bots](https://euphoria.io/room/bots/) for you to program.

If you need help, you can ask @myhandsaretypingwords, @jedevc, or any of the other awesome Euphorians in [&programming](https://euphoria.io/room/programming/) for help with any bot-related questions.

Have fun, and please be respectful!

@BotBot complies with the [Euphorian bot standards](https://github.com/jedevc/botrulez/blob/master/README.md).
