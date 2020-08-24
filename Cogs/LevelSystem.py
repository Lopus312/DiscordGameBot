import discord, random
from discord.ext import commands
from discord import User
from __main__ import server_settings

class LevelSystem(commands.Cog):


    def __init__(self,client):
        self.client = client


    @commands.command()
    async def profile(self,ctx, user: User = None):

        channel_check = await self.allowed_channel(ctx.guild,ctx.message.channel)
        if channel_check != True:
            await ctx.send( "{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel_check.mention ) )
            return

        embed = discord.Embed(
            title='Profile',
            color=discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)),
        )
        if user == None:
            user = ctx.author

        embed.add_field(name='Unique wins',value=5)
        embed.add_field(name='Unique losses',value=8)
        embed.add_field(name='Unique w/l ratio',value=0.6)
        embed.add_field(name='Wins',value=20)
        embed.add_field(name='Losses',value=10)
        embed.add_field(name='w/l ratio',value=2)
        embed.add_field(name='draws',value=3)
        embed.add_field(name='surrenders',value=0)
        embed.add_field(name='Played games',value=43)

        embed.set_author(name=user.name,icon_url=user.avatar_url)
        await ctx.send(user.mention,embed=embed)

    # checking whether this channel is allowed to receive game-related commands
    # Returns "True" or "channel" where game-related commands are allowed
    async def allowed_channel(self,guild,channel):
        if str(guild.id) not in server_settings:
            await main.settings_defaults(guild.id)
            return True
        elif str(server_settings[str(guild.id)]["game_channel"])!=str(channel.id) and server_settings[str( guild.id )]["game_channel"] != None:
            # return channel where game-related commands are allowed
            return self.client.get_channel(server_settings[str(guild.id)]["game_channel"])
        return True

def setup(client):
    client.add_cog( LevelSystem( client ) )