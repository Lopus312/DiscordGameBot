import discord, random
from discord.ext import commands
from discord import User, Member
from __main__ import server_settings
from Cogs.Classes.Stats import Stats as StatEdit
import __main__ as main


class Stats(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.has_permissions( administrator=True )
    @commands.command()
    async def statedit_win(self,ctx,user:User):
        StatEdit.win(StatEdit,ctx.guild,user)

    @commands.has_permissions( administrator=True )
    @commands.command()
    async def statedit_loss(self, ctx, user: User):
        StatEdit.loss(StatEdit, ctx.guild, user)

    @commands.has_permissions( administrator=True )
    @commands.command()
    async def statedit_surrender(self, ctx,user:User):
        StatEdit.surrender( StatEdit,ctx.guild, user)


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

    # checking whether this channel is allowed to receive game-related commands
    # Returns "True" or "channel" where game-related commands are allowed
    async def allowed_channel(self,guild,channel):
        if str(guild.id) not in server_settings:
            await main.settings_defaults(guild.id)
            return True
        elif str(server_settings[str(guild.id)]["game_channel"])!=str(channel.id) and server_settings[str( guild.id )]["game_channel"] != None:
            # return channel where game-related commands are allowed
            return True if self.client.get_channel(server_settings[str(guild.id)]["game_channel"]) == None else self.client.get_channel(server_settings[str(guild.id)]["game_channel"])
        return True

def setup(client):
    client.add_cog( Stats( client ) )