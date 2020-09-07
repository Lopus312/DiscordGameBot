# DiscordGameBot
Multi-functional Discord bot for many things, I use him primarily to learn python and working with API's. But if you'd like any of the features separately or anything else, feel free to download the source code

| Command | Aliases | Description |
| --- | --- | --- |
| `connectfour <user mention>` | `c4` `cfour` `connect4` `connect_four` | Creates a game of [Connect Four](https://en.wikipedia.org/wiki/Connect_Four) |
| `ping` | None | Bot will respond with his latency |
| `flip` | None | Bot will repond with either "Head" or "Tails", there is 50/50 chance on both of them|
| `profile [user]` | `stats` `statistics` | Shows stats for specified user |
| `uniques [user]` | None | Shows unique players user won/lost against |
| `statedit <surrender \| draw \| win \| loss> < add \| + \| - \| remove > <user>` | None | Administrator-only. Modifies stat for user |
| `settings` | `preferences` `prefs` `setup` | Administrator-only command. Opens settings menu where you can select which channel will be user for game-commands etc. |
| `purge [amount=2]` | `delete` | Administrator-only command. Deletes the specified number of messages from channel where this message was sent (default=2)|

## Hosting by yourself
### Requirements
python3.5.3 or higher, [discord.py](https://github.com/Rapptz/discord.py)

### Hosting

```
# Windows
py DiscordBot2.py

# Linux/Mac
python3 DiscordBot2.py
```

# Credits
[vbe0201](https://gist.github.com/vbe0201) for making [music cog](https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d)
