import discord
from discord.ext import commands
from datetime import datetime
import __main__ as main



class Hangman(commands.Cog):

    def __init__(self,client):
        self.client = client


    async def hangman(self,ctx):
        await ctx.send("Penis")

def setup(client):
    client.add_cog( Hangman( client ) )