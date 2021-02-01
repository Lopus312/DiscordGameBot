import discord, random, re
from discord.ext import commands
from datetime import datetime

# message for adding roles
random.seed(datetime.now())

msg = discord.Message
reactions = []
roles = []

class RoleMsg(commands.Cog):
    def __init__(self,client):
        self.client = client


    @commands.command(aliases=["role_msg"])
    async def rolemsg(self,ctx):
        global msg
        embed = discord.Embed(
        title = "SERVER ROLES",
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)),
        description="Use role_add <emote> <role_id>"
        )

        msg = await ctx.send(embed=embed)

    @commands.command(aliases=["roleadd"])
    async def role_add(self,ctx,reaction, role_id):
        global msg, reactions
        # Get role
        role = get_role(self.client, msg.guild, role_id)
        if role == None:
            await ctx.send(f"{ctx.author.mention} Invalid role")
            return

        emoji = discord.utils.get(msg.guild.emojis,name=reaction)

        await msg.add_reaction(emoji)
        embed = msg.embeds[0]
        embed.description = "React to this message to get role!"
        embed.add_field(name=role.name, value=emoji)

        reactions.append(emoji)
        roles.append(role)

        msg = await msg.edit(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user.id == self.client.user.id or reaction.message.id != msg.id:
            return

        for react in reactions:
            if react == reaction.emoji:
                role = roles[reactions.index(react)]
                await user.add_roles(role)


def isAdmin(user):
    for role in user.roles:
        if role.permissions.administrator==True:
            return True
    return False

def get_role(client, g,role):
    # try to get guild from g
    if type(g) == discord.Guild:
        guild = g
    elif client.get_guild(int(g)) != None:
        guild = client.get_guild(int(g))
    else:
        print('Error: get_role couldn\'t find guild {}.'.format(g),error=True,log=True)
        return None

    for role_ in guild.roles:
        # by mention
        if role == role_.mention:
            return role_
        # by id
        if role == role_.id:
            return role_
        # by name
        if role == role_.name:
            return role_

    # finding by name 2nd try
    if str(role)[0] == '@':
        role = role[1:]
    for role_ in guild.roles:
        if role == role_.name:
            return role_
    return None

def setup(client):
    client.add_cog( RoleMsg( client ) )