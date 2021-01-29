import discord, sys, os, traceback,json, random
from discord.ext import commands,tasks
from datetime import datetime
from Cogs.Classes.Stats import Stats as Stats
import Utils

client = commands.Bot(command_prefix="%", case_insensitive=True)
client.remove_command('help')
players = {}

# Cogs
extensions = ['Utils',"Cogs.Music","Cogs.Stats",'Cogs.GameManager','Cogs.RoleMsg']


# Default Settings
max_purge = 20
game_channel = "None"
music_channel = "None"

if os.path.exists("server_settings.json"):
    f = open("server_settings.json","r")
    server_settings=json.load(f)
    f.close()
else:
    server_settings = dict()

if os.path.exists("stats.json"):
    f = open("stats.json","r")
    Stats.set_stat_dict(Stats,json.load(f))
    f.close()
else:
    Stats.set_stat_dict(Stats,dict())

# message on bot start
@client.event
async def on_ready():
    Utils.print_date('Logged in as {0.user}'.format( client ),log=True)
    await client.change_presence(status=discord.Status.online,activity=discord.Activity(name="Corona Royale",type=5))
    update.start()

# removes specified number of messages
@commands.has_permissions(manage_messages=True)
@client.command()
async def purge(ctx, amount:int=2):
    if not isAdmin(ctx):
        await ctx.send("{} sorry, but you are not admin so you can't do that".format(ctx.author.mention))
        return

    if amount < max_purge:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.send('You can\'t purge that many message at once!, Maximum is set to **{}**'.format(max_purge))

# flip a coin
@client.command()
async def flip(ctx):
    if random.randint( 0, 1 ) == 1:
        await ctx.send( 'Head' )
    else:
        await ctx.send( 'Tails' )

#Ping-Pong
@commands.has_permissions(send_messages=True)
@client.command()
async def ping(ctx):
    await ctx.send( 'Pong! (%.2fms)' % (client.latency * 1000) )

# basic help command, prints available messages to user, will differ if user is admin or not
@client.command()
async def help(ctx):
    helpEmbed = discord.Embed(
        title='Game bot',
        description='Discord bot that you can use to play game of Connect 4. It is recommended for you to look at `settings` command first before using this bot (only administrator can use it). Argument inside `<>` means that it is required, inside `[]` is optional argument. This bot also has implemented audio playing from youtube, but this feature is buggy and not primary function of this bot.',
        color=discord.Colour.blue(),
    )

    try:
        helpEmbed.set_author(name=client.user.name,icon_url=client.user.avatar_url)
    except:
        Utils.print_date("Cannot get bot's avatar",error=True)
        helpEmbed.set_author( name=client.user.name, icon_url=discord.Embed.Empty )

    helpEmbed.add_field(name=":game_die:Games",value="`connectfour <user mention>` `profile [user]` `uniques [user]` `surrender`")
    helpEmbed.add_field(name=":notes:Music",value="`play <title>` `skip` `queue [page]` `join` `summon [channel]` `leave` `loop` `now` `pause` `resume` `stop` `shuffle` `remove <index>`")
    helpEmbed.add_field(name=":jigsaw:Other",value="`ping` `flip`")
    helpEmbed.add_field(name="Links",value="[Github](https://github.com/Lopus312/DiscordGameBot) | [Twitter](https://twitter.com/lopus312) | [Bot invite](https://discord.com/api/oauth2/authorize?client_id=679396653815562241&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FTgKJQW&scope=bot)")
    helpEmbed.set_footer(text="author: Lopus312")
    # Admin-only commands
    if isAdmin(ctx):
        helpEmbed.set_field_at(2,name=helpEmbed.fields[2].name,value=helpEmbed.fields[2].value+" `settings`\n`purge [amount]` `statedit <stat> <operation> <user>`")
    await ctx.send(embed=helpEmbed)

# Fore-saving all settings, only I as an author can use it
@client.command()
async def save(ctx):
    if str(ctx.author.id) == '293806543042904068':
        Utils.print_date('Warning: Force-save used guild:{}({}), player:{}({})'.format(ctx.guild.name,ctx.guild.id,ctx.author.name,ctx.author.id),warning=True,log=True)
        await save_settings()
        await ctx.send( "Settings force-saved" )


# Either shows or edits settings, based on if args are present or not
@client.command(aliases=['setting','preferences','prefs','setup'])
async def settings(ctx,*args):
    if not isAdmin(ctx):
        return

    if len(args) == 0:
        await settings_show(ctx)
    elif len(args) > 1:
        await settings_edit(ctx,args[0],args[1])

# Shows available settings
async def settings_show(ctx):
    guild_id = str( ctx.guild.id )

    if guild_id not in server_settings:
        await settings_defaults(guild_id)

    # one-value settings
    server_max_purge = server_settings[guild_id]["max_purge"]
    server_admin_role = get_role(guild_id,server_settings[guild_id]['admin_role'])
    if type(server_admin_role) == discord.Role:
        server_admin_role = server_admin_role.name

    # Settings containing list

    # Music channels
    if len(server_settings[str(ctx.guild.id)]["music_channel"]) > 0:
        names = list()
        for channel in server_settings[str(ctx.guild.id)]["music_channel"]:
            names.append(client.get_channel(channel).name)
        server_music_channel = str()
        server_music_channel += '", "'.join(names)
    else:
        server_music_channel = 'All'
    # Game channels
    if len(server_settings[str(ctx.guild.id)]["game_channel"]) > 0:
        names = list()
        for channel in server_settings[str(ctx.guild.id)]["game_channel"]:
            names.append(client.get_channel(channel).name)
        server_game_channel = str()
        server_game_channel += '", "'.join(names)
    else:
        server_game_channel = 'All'

    embed = discord.Embed(
        title='Settings',
        description='use `settings [name] [value]` to change values. **Channels** accept either channel id\'s, channel names or if it is text channel, mentions. Emotes in channel names might result in not finding that channel. If that\'s the case, use id instead. **Roles** accept ids, mentions or names',
        color=discord.Colour.blue(),
    )
    embed.add_field(name='Max_purge = "{}"'.format(server_max_purge),value="Maximum messages that can be removed by `purge` command", inline=False)
    embed.add_field(name='Game_channel = "{}"'.format(server_game_channel),value="Channel where bot will accept **Game** related commands. Use *'game_channel_remove' or 'game_channel-'* to remove channel from list also 'gch' can be used instead of 'game_channel' in any command", inline=False)
    embed.add_field(name='Music_channel = "{}"'.format(server_music_channel),value="Channel where bot will accept **Music** related commands. Use *'music_channel_remove' or 'music_channel-'* to remove channel from list also 'mch' can be used instead of 'music_channel' in any command", inline=False)
    embed.add_field(name='Admin_role = "{}"'.format(server_admin_role),value="This role will be able to use administrator-only commands from this bot", inline=False)
    await ctx.send(ctx.author.mention,embed=embed)

async def settings_edit(ctx,arg,value):
    arg = arg.lower()
    guild_id = str(ctx.guild.id)
    #
    #   General settings
    #
    if arg == "max_purge" or arg == 'mp':
        if guild_id not in server_settings:
            await settings_defaults(ctx.guild.id)
        if 'max_purge' in server_settings[guild_id]:
            server_settings[guild_id]['max_purge'] = value
            await settings_show(ctx)
        return
    if arg == 'admin_role' or arg == 'admin' or arg == 'ar':
        if guild_id not in server_settings:
            await settings_defaults(ctx.guild.id)
        if 'admin_role' in server_settings[guild_id]:
            role = get_role(guild_id,value)
            if role != None:
                server_settings[guild_id]['admin_role'] = role.id
                await settings_show(ctx)
        return
    #
    #   Channel settings
    #
    channel = await get_channel(ctx,value)
    if channel == None:
        await ctx.send("{} {} is not a channel, try again".format(ctx.author.mention,value))
        return

    if arg == 'game_channel' or arg == 'gch' or arg == 'gch+':
        if str(guild_id) not in server_settings:
            await settings_defaults(ctx.guild.id)
        if 'game_channel' in server_settings[guild_id]:
            server_settings[guild_id]['game_channel'].append(channel.id)
            await settings_show(ctx)
            return
    elif arg == 'game_channel_remove' or arg == 'game_channel-' or arg == 'gch-' or arg == 'gch_remove':
        if str(guild_id) not in server_settings:
            await settings_defaults(ctx.guild.id)
            return
        if 'game_channel' in server_settings[guild_id]:
            try:
                server_settings[guild_id]['game_channel'].remove(channel.id)
            except ValueError:
                await ctx.send("{} {} is not in game channel list, try again".format(ctx.author.mention,channel.name))
            else:
                await settings_show(ctx)
                return

    elif arg == 'music_channel' or arg == 'mch' or arg == 'mch+':
        if str(guild_id) not in server_settings:
            await settings_defaults(ctx.guild.id)
        if 'music_channel' in server_settings[guild_id]:
            server_settings[guild_id]['music_channel'].append(channel.id)
            await settings_show(ctx)
            return
    elif arg == 'music_channel_remove' or arg == 'music_channel-' or arg == 'mch-' or arg == 'mch_remove':
        if str(guild_id) not in server_settings:
            await settings_defaults(ctx.guild.id)
            return
        if 'music_channel' in server_settings[guild_id]:
            try:
                server_settings[guild_id]['music_channel'].remove(channel.id)
            except ValueError:
                await ctx.send("{} {} is not in music channel list, try again".format(ctx.author.mention,channel.name))
            else:
                await settings_show(ctx)
                return

    elif arg == 'music_channel':
        if guild_id not in server_settings:
            await settings_defaults(ctx.guild.id)
        if 'music_channel' in server_settings[guild_id]:
            server_settings[guild_id]['music_channel'].append(channel.id)
            await settings_show(ctx)
            return

async def settings_defaults(guild_id):
    if guild_id in server_settings:
        Utils.print_date('Error: settings_defaults was called on guild that is already in settings, settings overwrite prevented',error=True,log=True)
        return
    dict_max_purge = dict()
    dict_music_channel = dict()
    dict_game_channel = dict()
    dict_admin_role = dict()

    dict_max_purge["max_purge"] = str(max_purge)
    dict_music_channel["music_channel"] = []
    dict_game_channel["game_channel"] = []
    dict_admin_role["admin_role"] = None

    server_settings[str(guild_id)] = dict()
    server_settings[str(guild_id)] = dict_max_purge
    server_settings[str(guild_id)].update( dict_game_channel )
    server_settings[str(guild_id)].update(dict_music_channel)
    server_settings[str(guild_id)].update(dict_admin_role)

async def save_settings():
    Utils.print_date( "Saving settings..." )
    f = open( 'server_settings.json', 'w+' )
    json.dump( server_settings, f )
    f.close()
    f = open( 'stats.json', 'w+' )
    json.dump( Stats.get_stat_dict(Stats), f )
    f.close()
    Utils.print_date( "Saved settings" )

# Attempt to get channel from string
async def get_channel(ctx, string):
    channel = None
    # Try if string is channel id
    try:
        channel = client.get_channel(int(string))
    except ValueError:
        pass
    if channel != None:
        return channel

    # Try if string is channel mention
    for channel_ in ctx.guild.text_channels:
        if str(channel_.mention) == string:
            return channel_
    # Try if string is channel name
    for channel_ in ctx.guild.text_channels:
        if str(channel_.name) == string:
            return channel_
    return None

def get_role(g,role):
    # try to get guild from g
    if type(g) == discord.Guild:
        guild = g
    elif client.get_guild(int(g)) != None:
        guild = client.get_guild(int(g))
    else:
        Utils.print_date('Error: get_role couldn\'t find guild {}.'.format(g),error=True,log=True)
        return None

    for role_ in guild.roles:
        # by mention
        if role == role_.mention:
            return role_
        # by id
        if role == role_.id:
            return role_
        # by name
        if role == role_.name:
            return role_

    # finding by name 2nd try
    if str(role)[0] == '@':
        role = role[1:]
    for role_ in guild.roles:
        if role == role_.name:
            return role_
    return None

@tasks.loop(minutes=30.0)
async def update():
    await save_settings()

@client.event
async def on_command_error(ctx,error):
    #Command not found
    if isinstance(error,commands.errors.CommandNotFound):
        Utils.print_date(error,error=True)
        await ctx.send('This command does not exist, try `%help` for a list of available commands')
        return
    #Every other error
    Utils.print_date('Command error({}):{}'.format(type(error),error),error=True,log=True)
    await ctx.send(error)

def isAdmin(ctx):
    for role in ctx.author.roles:
        if role.permissions.administrator==True:
            return True
        elif str(ctx.guild.id) in server_settings and role.id == server_settings[str(ctx.guild.id)]["admin_role"]:
            return True

    return False
# Loading all the cogs
if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            Utils.print_date('{} loaded.'.format(extension))
        except Exception as error:
            Utils.print_date(('{} cannot be loaded. [{}]'.format(extension,error)))

client.run(open("TOKEN.txt","r").read())
