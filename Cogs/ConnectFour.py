import discord
from discord.ext import commands, tasks
from discord import User
from datetime import datetime

c4_time = 30

games = dict()
timer_messages = [[],[],[]]
game = [[':white_large_square:']*7]*6

template_embed=discord.Embed(
        title='Connect Four',
        color=discord.Colour.from_rgb(225,94,235),
    )

class ConnectFour(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.update.start()

    @commands.command()
    async def connectfour(self,ctx, user: User):
        await create_game(ctx,user)

    @commands.command()
    async def ConnectFour(self, ctx, user: User):
        await create_game( ctx, user )

    @commands.command()
    async def connectFour(self, ctx, user: User):
        await create_game( ctx, user )

    @commands.command()
    async def c4(self, ctx, user: User):
        await create_game( ctx, user )

    @commands.command()
    async def cfour(self, ctx, user: User):
        await create_game( ctx, user )

    @commands.command()
    async def cFour(self, ctx, user: User):
        await create_game( ctx, user )


    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user.id == self.client.user.id or user.id not in timer_messages[2]:
            return
        # Accepted game
        if reaction.emoji == '\U00002705':
            ix = timer_messages[2].index( user.id )
            message = timer_messages[0][ix]
            timer_messages[0].remove( timer_messages[0][ix] )
            timer_messages[1].remove( timer_messages[1][ix] )
            timer_messages[2].remove( timer_messages[2][ix] )
            await reaction.message.channel.send(embed = create_embed())
            await message.delete()

    @tasks.loop( seconds=1.0 )
    async def update(self):
        if len(timer_messages[0])==0:
            return
        for x in range( len( timer_messages[0] ) ):
            try:
                message = timer_messages[0][x]
                message_str = message.content.replace( '{}s'.format(timer_messages[1][x]), '{}s'.format(timer_messages[1][x]-1) )
                await message.edit( content=message_str )
                if timer_messages[1][x] > 1:
                    timer_messages[1][x] -= 1
                else:
                    timer_messages[0].remove( timer_messages[0][x] )
                    timer_messages[1].remove( timer_messages[1][x] )
                    timer_messages[2].remove( timer_messages[2][x] )
            except IndexError:
                print(IndexError)

async def create_game(ctx,user:User):
    global games,timer_messages
    # if either of users is already in game, prevent starting another one
    if ctx.guild.id in games:
        if ctx.author.id in games[ctx.guild.id]:
            await ctx.send( ctx.author.mention + ' you are already in game, finish it before starting another one please.' )
            return
        elif user.id in games[ctx.guild.id]:
            await ctx.send( user.name + ' is already in game, wait for him to finish before challenging him' )
            return

    message = await ctx.send("{} you were challenged to a game of **Connect Four**! you have **{}s** to react to this messsage".format(user.mention,c4_time))
    timer_messages[0].append(message)
    timer_messages[1].append(c4_time)
    timer_messages[2].append(user.id)

    await message.add_reaction("\U00002705")
    await message.add_reaction("\U0001F6AB")

def create_embed():
    embed = template_embed
    embed_desc = ""
    for x in range( len( game ) ):
        for y in range( len( game[x] ) ):
            embed_desc += game[x][y]
        embed_desc += '\n'
    embed.description = embed_desc
    return embed



def setup(client):
    client.add_cog( ConnectFour( client ) )

class Game:
    def __init__(self,user_A,user_B):
        self.user_A = user_A
        self.user_B = user_B

