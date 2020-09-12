import discord, gc
from discord.ext import commands, tasks
from datetime import datetime
import __main__ as main
from __main__ import server_settings
import Utils

# ConnectFour Cog
c4 = None
# Hangman
hm = None
x = 5
Cogs = ['Cogs.ConnectFour','Cogs.Hangman']
# Countdown messages
invite_messages = [[],[],[],[]]

class GameManager(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.update.start()
        self.invite_messages = invite_messages

    @commands.command()
    async def surrender(self,ctx):
        await c4.surrender(ctx)

    @commands.command(aliases=['hm','hangwomen','hw'])
    async def hangman(self,ctx):
        await hm.hangman(ctx)

    # Creates invite if both users meet requirements
    @commands.command(aliases=['cfour','connect4','connectfour','connect_four'])
    async def c4(self, ctx, user: discord.User = None):

        if await c4.can_i_create_invite(ctx,user):
            # creating cooldown message
            message = await ctx.send("{} you were challenged to a game of **Connect Four**! you have **{}s** to react to this message".format(user.mention,c4.cd_time))
            invite_messages[0].append(message)
            invite_messages[1].append(c4.cd_time)
            invite_messages[2].append(user.id)
            invite_messages[3].append(ctx.author.id)
            # Adding tick and cross reaction
            await message.add_reaction("\U00002705")
            await message.add_reaction("\U0001F6AB")

    @commands.command(aliases=['find','mygame','mygames','lookupgame','lookup','fmg'])
    async def findmygame(self,ctx):
        print(x)
        if ctx.guild.id in c4.games:
            if ctx.author.id in c4.games[ctx.guild.id]:
                msg = c4.games[ctx.guild.id][ctx.author.id].msg
                link = 'https://discordapp.com/channels/{}/{}/{}'.format(ctx.guild.id,msg.channel.id,msg.id)
                await Utils.send_embed(ctx.channel,text=ctx.author.mention,title='Find My Game',desc='Command that helps you find where you left your game opened. **Does not work on mobile**',name='Games:',value='[Connect Four]({})'.format(link))
                return

        await ctx.send('{} You are not in any game right now'.format(ctx.author.mention))

    @tasks.loop( seconds=1.0 )
    async def update(self):
        # countdown message
        # 0=message, 1=time, 2=challenged player, 3=challenger
        global invite_messages
        if len(invite_messages[1])==0:
            return
        for x in range( len( invite_messages[1] ) ):
            try:
                message = invite_messages[0][x]
                message_str = message.content.replace( '{}s'.format(invite_messages[1][x]), '{}s'.format(invite_messages[1][x]-1) )
                await message.edit( content=message_str )
                if invite_messages[1][x] > 1:
                    invite_messages[1][x] -= 1
                else:
                    message = invite_messages[0][x]
                    await message.edit( content='{} {} did not accept your invite'.format(self.client.get_user(invite_messages[3][x]).mention,self.client.get_user(invite_messages[2][x]).name))
                    invite_messages[0].remove( invite_messages[0][x] )
                    invite_messages[1].remove( invite_messages[1][x] )
                    invite_messages[2].remove( invite_messages[2][x] )
                    invite_messages[3].remove( invite_messages[3][x] )
            except IndexError:
                pass
            except discord.errors.NotFound:
                Utils.print_date('discord.NotFound Error Handled: Someone most likely removed invite message for c4, removing from message list... \n\tmessage:{}\n\ttime:{}\n\tauthor:{}\n\tplayer:{}'.format(invite_messages[0][x],invite_messages[1][x],invite_messages[2][x],invite_messages[3][x]),warning=True,log=True)
                invite_messages[0].remove( invite_messages[0][x] )
                invite_messages[1].remove( invite_messages[1][x] )
                invite_messages[2].remove( invite_messages[2][x] )
                invite_messages[3].remove( invite_messages[3][x] )

    async def invite_remove(self,user_id):
        ix = invite_messages[2].index( user_id )
        message = invite_messages[0][ix]
        invite_messages[0].remove( invite_messages[0][ix] )
        invite_messages[1].remove( invite_messages[1][ix] )
        invite_messages[2].remove( invite_messages[2][ix] )
        invite_messages[3].remove( invite_messages[3][ix] )
        await message.delete()

    def get_invite_messages(self):
        return invite_messages

def setup(client):
    # Loading this cog
    client.add_cog( GameManager( client ) )
    # Loading cogs in Cogs list
    for Cog in Cogs:
        try:
            client.load_extension( Cog )
            Utils.print_date( '{} loaded.'.format( Cog ) )
        except Exception as error:
            Utils.print_date( ('{} cannot be loaded. [{}]'.format( Cog, error )),error=True )
    # Getting ConnectFour Cog
    global c4,hm
    c4 = client.get_cog( 'ConnectFour' )
    hm = client.get_cog( 'Hangman' )




