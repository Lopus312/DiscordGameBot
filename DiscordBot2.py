import discord, sys, os
from discord.ext import commands
from datetime import datetime

client = commands.Bot(command_prefix="%")
client.remove_command('help')
players = {}

# Cogs
extensions = ['Cogs.Utils','Cogs.ConnectFour',"Cogs.Music"]

# Settings
max_purge = 20

def add_date(string):
    return datetime.now().strftime("%H:%M:%S")+" "+string

# message on bot start
@client.event
async def on_ready():
    print(add_date('Logged in as {0.user}'.format( client )))

# removes specified number of messages
@commands.has_permissions(manage_messages=True)
@client.command(name='purge',brief='removes last two messages, optional one argument specifying number of messages (%purge 5)',description='by default, removes last two messages. Can be used with argument specifying how many messages should be deleted (ex. "%purge 5" will remove last 5 messages). Keep in mind that command it self is message')
async def purge(ctx, amount=2):
    if amount < max_purge:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.send('You can\'t purge that many message at once!, Maximum is set to **{}**'.format(max_purge))

#Ping-Pong
@client.command(name='ping',brief='Bot replies with his ping', description='Bot will respond with "Pong!" followed by bots latency in *ms* ')
async def ping(ctx):
    await ctx.send( 'Pong! (%.2fms)' % (client.latency * 1000) )

def isAdmin(ctx):
    for role in ctx.author.roles:
        if role.permissions.administrator==True:
            return True

    return False

@client.command()
async def help(ctx):
    descr = ''
    for command in client.commands:
        if(command.brief!=None):
            descr+="`{}`: {}\n".format(command.name,command.brief)

    helpEmbed = discord.Embed(
        title='Commands',
        description=descr,
        color=discord.Colour.blue(),
    )
    helpEmbed.set_thumbnail(url="https://cdn.discordapp.com/avatars/679396653815562241/9e600c78ba524a7c3262cd0ffa6f999c.png")

    await ctx.send(embed=helpEmbed)


# Loading all the cogs
if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            print(add_date('{} loaded.'.format(extension)))
        except Exception as error:
            print(('{} cannot be loaded. [{}]'.format(extension,error)))


client.run(open("TOKEN.txt","r").read())
