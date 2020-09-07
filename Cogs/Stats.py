import discord, random
import __main__ as main
from discord.ext import commands
from discord import User, Member
from __main__ import server_settings
from Cogs.Classes.Stats import Stats as StatEdit



class Stats(commands.Cog):

    def __init__(self,client):
        self.client = client

    # statedit win add user
    @commands.has_permissions( administrator=True )
    @commands.command()
    async def statedit(self,ctx,what_,operation_,user:User):
        what = what_.strip().lower()
        operation = operation_.strip().lower()

        if what == 'surrender' or what=='surrenders':
            if operation == 'add' or operation == '+':
                StatEdit.surrender(StatEdit,ctx.guild,user)
            elif operation == 'remove' or operation == '-':
                StatEdit.surrender(StatEdit,ctx.guild,user,remove=True)

        elif what == 'draw' or what == 'draws':
            if operation == 'add' or operation == '+':
                StatEdit.draw( StatEdit, ctx.guild, user )
            elif operation == 'remove' or operation == '-':
                StatEdit.draw( StatEdit, ctx.guild, user, remove=True )

        elif what == 'win' or what == 'wins':
            if operation == 'add' or operation == '+':
                StatEdit.win( StatEdit, ctx.guild, user ,chk_loss=False)
            elif operation == 'remove' or operation == '-':
                StatEdit.win( StatEdit, ctx.guild, user, remove=True,chk_loss=False )

        elif what == 'loss' or what == 'lose' or what=='losses':
            if operation == 'add' or operation == '+':
                StatEdit.loss( StatEdit, ctx.guild, user, chk_win=False )
            elif operation == 'remove' or operation == '-':
                StatEdit.loss( StatEdit, ctx.guild, user, remove=True, chk_win=False )
        else:
            await ctx.send("Unknown arguments, ***first is what you want to edit*** (*'surrenders'*,*'draws'*,*'wins'* or *'losses'*) ***and second how*** (*'add'* or *'remove'*).\n example: **%statedit wins add** @{}".format(ctx.author.mention))

    @commands.command(aliases=["stats","statistics"])
    async def profile(self,ctx, user: User = None):
        # Check if channel can be used for game-related commands
        channel_check = await self.allowed_channel(ctx.guild,ctx.message.channel)
        if channel_check != True:
            await ctx.send( "{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel_check.mention ) )
            return
        # if user is not specified, it is the author
        if user == None:
            user = ctx.author
        guild = ctx.author.guild

        StatEdit.createDefaults( StatEdit, guild, user )
        stat_dict = StatEdit.get_stat_dict( StatEdit )

        # Creating and sending embed
        embed = discord.Embed(
            title='Profile',
            color=discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)),
        )

        embed.add_field(name='Unique players defeated',value=len(stat_dict[str( guild.id )][str(user.id)]["unique_wins"]))
        embed.add_field(name='Unique players crushed by',value=len(stat_dict[str( guild.id )][str(user.id)]["unique_losses"]))
        # Preventing division by zero error
        if int(len(stat_dict[str( guild.id )][str(user.id)]["unique_losses"])) != 0:
            embed.add_field(name='Unique w/l ratio',value=int(len(stat_dict[str( guild.id )][str(user.id)]["unique_wins"]))/int(len(stat_dict[str( guild.id )][str(user.id)]["unique_losses"])))
        else: embed.add_field(name='Unique w/l ratio',value=0.0)

        embed.add_field(name='Wins',value=stat_dict[str( guild.id )][str(user.id)]["wins"])
        embed.add_field(name='Losses',value=stat_dict[str( guild.id )][str(user.id)]["losses"])

        if int(stat_dict[str( guild.id )][str(user.id)]["losses"]) != 0:
            embed.add_field(name='w/l ratio',value=int(stat_dict[str( guild.id )][str(user.id)]["wins"])/int(stat_dict[str( guild.id )][str(user.id)]["losses"]))
        else:
            embed.add_field( name='w/l ratio', value=0.0)

        embed.add_field(name='draws',value=stat_dict[str( guild.id )][str(user.id)]["draws"])
        embed.add_field(name='surrenders',value=stat_dict[str( guild.id )][str(user.id)]["surrenders"])
        embed.add_field(name='Played games',value=stat_dict[str( guild.id )][str(user.id)]["games"])

        embed.set_author(name=user.name,icon_url=user.avatar_url)
        await ctx.send(ctx.author.mention,embed=embed)

    @commands.command(alises=["unique"])
    async def uniques(self,ctx,user:User = None):
        stat_dict = StatEdit.get_stat_dict( StatEdit )
        if user == None:
            user = ctx.author
        # wins
        if len( stat_dict[str( ctx.guild.id )][str(user.id)]["unique_wins"] ) > 0:
            wins = str()
            for win in stat_dict[str( ctx.guild.id )][str(user.id)]["unique_wins"]:
                user_ = self.client.get_user(win)
                if  user_ != None:
                    wins += ', {}'.format(user_.name)
            wins = wins[2:]
        else:
            wins=None
        # losses
        if len( stat_dict[str( ctx.guild.id )][str(user.id)]["unique_losses"] ) > 0:
            losses = str()
            for loss in  stat_dict[str( ctx.guild.id )][str(user.id)]["unique_losses"]:
                user_ = self.client.get_user(loss)
                if user_ != None:
                    losses += ', {}'.format(user_.name)
            losses = losses[2:]
        else:
            losses=None

        embed = discord.Embed(
            title='Uniques',
            color=discord.Colour.from_rgb( random.randint( 0, 255 ), random.randint( 0, 255 ), random.randint( 0, 255 ) ),
        )
        embed.add_field(name='Unique players defeated',value=wins)
        embed.add_field(name='Unique players crushed by',value=losses)
        embed.set_author( name=user.name, icon_url=user.avatar_url )
        await ctx.send(ctx.author.mention,embed=embed)



    # checking whether this channel is allowed to receive game-related commands
    # Returns "True" or "channel" where game-related commands are allowed
    async def allowed_channel(self,guild,channel):
        if str(guild.id) not in server_settings:
            await main.settings_defaults(guild.id)
            return True
        elif channel.id not in server_settings[str(guild.id)]["game_channel"] and len(server_settings[str(guild.id)]["game_channel"])>0:
            # return random channel where game-related commands are allowed
            return self.client.get_channel(server_settings[str(guild.id)]["game_channel"][random.randint(0,len(server_settings[str(guild.id)]["game_channel"])-1)])
        return True

def setup(client):
    client.add_cog( Stats( client ) )