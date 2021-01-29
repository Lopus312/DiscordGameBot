import discord
from discord.ext import commands

class RoleMsg(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command(aliases=["role_msg"])
    async def rolemsg(self,ctx,arg):
        try:
            msg = await ctx.fetch_message(arg)
        except discord.NotFound:
            await ctx.send('Could not find message')
        except discord.Forbidden:
            await ctx.send('Don\'t have permission to get this message')
        except discord.HTTPException:
            await ctx.send('Retrieving the message failed')

        first = msg.content.find(':')
        second = first+msg.content[first+1:].find(':')+2

        emoji = msg.content[first:second]
        print(f'{first}:{second}, {emoji},{msg.content}')
        await ctx.send(msg.content)
        #await ctx.send(emoji)

def setup(client):
    client.add_cog( RoleMsg( client ) )