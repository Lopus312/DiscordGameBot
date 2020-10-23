import discord, random,requests,Utils
from discord.ext import commands
from discord import User, Member
from __main__ import server_settings
import __main__ as main
from Cogs.Classes.Stats import Stats as StatEdit



class R6(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.command()
    async def r6(self,ctx,arg):

        x = requests.get(f'https://r6.apitab.com/search/uplay/{arg}')
        print(x)
        e = discord.Embed()
        s = ' '
        #if len(x.json()['players'])>1:
        #    for i,player in enumerate(x.json()['players']):
        #        e.title='R6 Search'
        #        s += f"`{i}.`\t{x.json()['players'][player]['profile']['p_name']}\n"
        #else:
        data = x.json()
        p_id = str(list(data['players'].keys())[0])
        print(p_id)
        e.title='R6 Profile'
        e.add_field(name='Name',value=data['players'][p_id]['profile']['p_name'])
        e.add_field(name='Level',value=data['players'][p_id]['stats']['level'])
        for thing,value in data['players'][p_id]['ranked'].items():
            if value != "" and value != 0:
                e.add_field(name=thing,value=value)
        e.description = s
        await ctx.send(embed=e)

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
    client.add_cog( R6( client ) )