import discord, sys, os, traceback,json
from discord.ext import commands,tasks
from datetime import datetime

client = commands.Bot(command_prefix="%", case_insensitive=True)
client.remove_command('help')
players = {}

# Cogs
extensions = ['Cogs.Utils','Cogs.ConnectFour',"Cogs.Music"]

# Default Settings
max_purge = 20
game_channel = "None"
music_channel = "None"

f = open("server_settings.json","r")
server_settings=json.load(f)
f.close()

def print_date(string,print_=True,error=False,log=False):
    if log:
        try:
            f = open( 'DiscordBot2_Log.txt', 'a+' )
            f.write("\n"+datetime.now().strftime("%H:%M:%S")+" "+string)
            f.close()
        except:
            print_date('Unexpected error: Could not write error to log file ({})'.format( string ), error=True )
    if error:
        str = '\033[0;31;48m'+datetime.now().strftime("%H:%M:%S")+" "+string+'\033[0;38;48m'
    else:
        str = datetime.now().strftime( "%H:%M:%S" ) + " " + string
    if print_:
        print(str)
    return str

# message on bot start
@client.event
async def on_ready():
    print_date('Logged in as {0.user}'.format( client ),log=True)
    update.start()

# removes specified number of messages
@commands.has_permissions(manage_messages=True)
@client.command(name='purge',brief='removes last two messages, optional one argument specifying number of messages (%purge 5)',description='by default, removes last two messages. Can be used with argument specifying how many messages should be deleted (ex. "%purge 5" will remove last 5 messages). Keep in mind that command it self is message')
async def purge(ctx, amount=2):
    if not isAdmin(ctx):
        await ctx.send("{} sorry, but you are not admin so you can't do that".format(ctx.author.mention))
        return

    if amount < max_purge:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.send('You can\'t purge that many message at once!, Maximum is set to **{}**'.format(max_purge))

#Ping-Pong
@commands.has_permissions(send_messages=True)
@client.command(name='ping',brief='Bot replies with his ping', description='Bot will respond with "Pong!" followed by bots latency in *ms* ')
async def ping(ctx):
    await ctx.send( 'Pong! (%.2fms)' % (client.latency * 1000) )

def isAdmin(ctx):
    for role in ctx.author.roles:
        if role.permissions.administrator==True:
            return True

    return False

@client.command()
async def save(ctx):
    # Only I can use this command
    if str(ctx.author.id) == '293806543042904068':
        await save_settings()
        await ctx.send( "Settings force-saved" )

@client.command()
async def settings(ctx,*args):
    if not isAdmin(ctx):
        return

    if len(args) == 0:
        await settings_show(ctx)
    elif len(args) > 1:
        await settings_edit(ctx,args[0],args[1])

async def settings_show(ctx):

    embed = discord.Embed(
        title='Settings',
        description='use `settings [name] [value]` to change values. **Channels** accept either channel id\'s, channel names or if it is text channel, mentions. Emotes in channel names might result in not finding that channel. If that\'s the case, use id instead. *With id\'s channel finding is faster* so it is recommended for larger servers ',
        color = discord.Colour.blue(),
    )

    try:
        guild_id = str(ctx.guild.id)
        server_max_purge = server_settings[guild_id]["max_purge"] if guild_id in server_settings else max_purge
        server_game_channel = server_settings[guild_id]["game_channel"] if guild_id in server_settings else game_channel
        server_music_channel = server_settings[guild_id]["music_channel"] if guild_id in server_settings else music_channel
    except:
        print_date("Error in setting_show function.\nServer list:{}\nTraceback:{}".format(server_settings,traceback.format_exc()),error=True,log=True)
        await ctx.send("Error occurred while trying to show settings, please contact author https://twitter.com/lopus312 with your server id and time when this happened (right click on your server and 'Copy ID')")
        server_max_purge = max_purge
        server_game_channel = game_channel
        server_music_channel = music_channel

    if server_game_channel != "None":
        server_game_channel = client.get_channel(server_settings[str(ctx.guild.id)]["game_channel"]).name
    if server_music_channel != "None":
        server_music_channel = client.get_channel( server_settings[str(ctx.guild.id)]["music_channel"] ).name

    embed.add_field(name='Max_purge = "{}"'.format(server_max_purge),value="Maximum messages that can be removed by `purge` command", inline=False)
    embed.add_field(name='Game_channel = "{}"'.format(server_game_channel),value="Channel where bot will accept **Game** related commands. If None, bot will listen everywhere where he has permission.", inline=False)
    embed.add_field(name='Music_channel = "{}"'.format(server_music_channel),value='Channel where bot will accept **Music** related commands. If None, bot will listen everywhere where he has permission.', inline=False)
    await ctx.send(ctx.author.mention,embed=embed)

async def settings_edit(ctx,arg,value):
    async with ctx.typing():
        arg = arg.lower()
        guild_id = str(ctx.guild.id)

        if arg == "max_purge":
            if guild_id not in server_settings:
                await settings_defaults(ctx.guild.id)
            if 'max_purge' in server_settings[guild_id]:
                server_settings[guild_id]['max_purge'] = value
                await settings_show(ctx)
            else:
                # this should never run, but just in case
                temp_dict = dict()
                temp_dict["max_purge"] = value
                server_settings[guild_id] = temp_dict
                await settings_show(ctx)

        # Only channel settings forward
        channel = await get_channel(ctx,value)
        if channel == None:
            await ctx.send("{} {} is not a channel, try again".format(ctx.author.mention,value))
            return

        if arg == 'game_channel':
            if guild_id not in server_settings:
                await settings_defaults(ctx.guild.id)
            if 'game_channel' in server_settings[guild_id]:
                server_settings[guild_id]['game_channel'] = channel.id
                await settings_show(ctx)
            else:
                temp_dict = dict()
                temp_dict['game_channel'] = channel.id
                server_settings[guild_id].update(temp_dict)
                await settings_show(ctx)
        if arg == 'music_channel':
            if guild_id not in server_settings:
                await settings_defaults(ctx.guild.id)
            if 'music_channel' in server_settings[guild_id]:
                server_settings[guild_id]['music_channel'] = channel.id
                await settings_show(ctx)
            else:
                temp_dict = dict()
                temp_dict['music_channel'] = channel.id
                server_settings[guild_id].update(temp_dict)
                await settings_show(ctx)

async def settings_defaults(guild_id):
    dict_max_purge = dict()
    dict_music_channel = dict()
    dict_game_channel = dict()

    dict_max_purge["max_purge"] = str(max_purge)
    dict_music_channel["music_channel"] = str(music_channel)
    dict_game_channel["game_channel"] = str(game_channel)

    server_settings[str(guild_id)] = dict()
    server_settings[str(guild_id)] = dict_max_purge
    server_settings[str(guild_id)].update( dict_game_channel )
    server_settings[str(guild_id)].update(dict_music_channel)

async def save_settings():
    print_date( "Saving server_settings..." )
    f = open( 'server_settings.json', 'w+' )
    json.dump( server_settings, f )
    f.close()
    print_date( "Saved server_settings" )

async def get_channel(ctx, string):
    channel = None
    try:
        channel = client.get_channel(int(string))
    except ValueError:
        pass

    if channel != None:
        return channel


    if string[0] == "#":
        string = string[1:]

    for channel_ in ctx.guild.text_channels:
        if str(channel_.name) == string:
            return channel_
    return None

@client.command()
async def help(ctx):

    helpEmbed = discord.Embed(
        title='Game bot',
        description='Discord bot that you can use to play game of Connect 4. It is recommended for you to look at `settings` command first before using this bot (only administrator can use it). This bot also has implemented audio playing from youtube, but this feature is buggy and not primary function of this bot.',
        color=discord.Colour.blue(),
    )

    try:
        helpEmbed.set_author(name=client.user.name,icon_url=client.user.avatar_url)
    except:
        print_date("Cannot get bot's avatar",error=True)
        helpEmbed.set_author( name=client.user.name, icon_url=discord.Embed.Empty )

    helpEmbed.add_field(name="Games",value="`connectfour`")
    helpEmbed.add_field(name="Music",value="`play [title]` `skip` `queue` `join` `summon [channel]` `leave` `now` `pause` `resume` `stop` `shuffle` `remove [index]`")
    helpEmbed.add_field(name="Other",value="`settings` `ping` `purge [amount]` `flip`")
    helpEmbed.set_footer(text="author: Lopus312")

    await ctx.send(embed=helpEmbed)

@tasks.loop(minutes=30.0)
async def update():
    await save_settings()



# Loading all the cogs
if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            print_date('{} loaded.'.format(extension))
        except Exception as error:
            print_date(('{} cannot be loaded. [{}]'.format(extension,error)))

client.run(open("TOKEN.txt","r").read())
