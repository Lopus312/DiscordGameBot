import discord

from discord.ext import commands

class Utils(commands.Cog):

    def __init__(self,client):
        self.client = client

    # flip a coin
    @commands.command(brief='flips a coin', description='Will randomly choose if respond with "head" or "tails"')
    async def flip(self,ctx):
        if random.randint( 0, 1 ) == 1:
            await ctx.send( 'head' )
        else:
            await ctx.send( 'tails' )



def setup(client):
    client.add_cog(Utils(client))
