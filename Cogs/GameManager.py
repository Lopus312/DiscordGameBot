import discord, gc
from discord.ext import commands, tasks
from datetime import datetime
import __main__ as main
from __main__ import server_settings
import Utils

# ConnectFour Cog
c4 = None
# Hangoman
hm = None
Cogs = ['Cogs.ConnectFour']
# Countdown messages

class GameManager(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.update.start()

    @commands.command()
    async def surrender(self,ctx):
        await c4.surrender(ctx)

    @commands.command(aliases=['hm','hangwomen','hw'])
    async def hangman(self,ctx):
        await ctx.send('Penis')

    # Creates invite if both users meet requirements
    @commands.command(aliases=['cfour','connect4','connectfour','connect_four'])
    async def c4(self, ctx, user: discord.User = None):

        if await c4.can_i_create_invite(ctx,user):
            # creating cooldown message
            message = await ctx.send("{} you were challenged to a game of **Connect Four**! you have **{}s** to react to this message".format(user.mention,c4.cd_time))
            c4.timer_messages[0].append(message)
            c4.timer_messages[1].append(c4.cd_time)
            c4.timer_messages[2].append(user.id)
            c4.timer_messages[3].append(ctx.author.id)
            # Adding tick and cross reaction
            await message.add_reaction("\U00002705")
            await message.add_reaction("\U0001F6AB")

    @tasks.loop( seconds=1.0 )
    async def update(self):
        # countdown message
        timer_messages = c4.timer_messages
        if len(timer_messages[1])==0:
            return
        for x in range( len( timer_messages[1] ) ):
            try:
                message = timer_messages[0][x]
                message_str = message.content.replace( '{}s'.format(timer_messages[1][x]), '{}s'.format(timer_messages[1][x]-1) )
                await message.edit( content=message_str )
                if timer_messages[1][x] > 1:
                    timer_messages[1][x] -= 1
                else:
                    message = timer_messages[0][x]
                    timer_messages[0].remove( timer_messages[0][x] )
                    timer_messages[1].remove( timer_messages[1][x] )
                    timer_messages[2].remove( timer_messages[2][x] )
                    timer_messages[3].remove( timer_messages[3][x] )
                    await message.delete()
            except IndexError:
                pass
            except discord.errors.NotFound:
                Utils.print_date('discord.NotFound Error Handled: Someone most likely removed invite message for c4, removing from message list... \n\tmessage:{}\n\ttime:{}\n\tauthor:{}\n\tplayer:{}'.format(timer_messages[0][x],timer_messages[1][x],timer_messages[2][x],timer_messages[3][x]),warning=True,log=True)
                timer_messages[0].remove( timer_messages[0][x] )
                timer_messages[1].remove( timer_messages[1][x] )
                timer_messages[2].remove( timer_messages[2][x] )
                timer_messages[3].remove( timer_messages[3][x] )

def setup(client):
    # Loading this cog
    client.add_cog( GameManager( client ) )
    # Loading cogs in Cogs list
    for Cog in Cogs:
        try:
            client.load_extension( Cog )
            Utils.print_date( '{} loaded.'.format( Cog ) )
        except Exception as error:
            Utils.print_date( ('{} cannot be loaded. [{}]'.format( Cog, error )) )
    # Getting ConnectFour Cog
    global c4,hm
    c4 = client.get_cog( 'ConnectFour' )




