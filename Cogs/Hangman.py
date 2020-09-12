import discord, Utils
from discord.ext import commands
from datetime import datetime
from __main__ import settings_defaults, server_settings

games = dict()

class Hangman(commands.Cog):

    def __init__(self,client):
        self.client = client


    async def hangman(self,ctx):
        # Create Game class
        gm = Game(ctx.author)

        await gm.setup(ctx.channel)
        # Save Game
        games_user = dict()
        games_user[ctx.author.id] = gm

        if ctx.guild.id in games:
            games[ctx.guild.id].update(games_user)
        else:
            games[ctx.guild.id] = games_user



    async def can_i_create_invite(self,ctx):
        if await self.is_dis_game_channel(ctx):
            # Checking if game can start
            if ctx.guild.id in games:
                if ctx.author.id in games[ctx.guild.id]:
                    await ctx.send( ctx.author.mention + ' you are already in game, finish it before starting another one please.' )
                    return False
                elif user.bot:
                    await ctx.send('bruh, '+ctx.author.mention+' you can\'t challenge a bot. you\'d be crushed and I can\'t allow you that fast defeat ')
                    return False
                elif  ctx.author.id == self.client.user.id:
                    await ctx.send('You dare to challenge me??! You are way too weak, I wont even try')
                    return False
                elif  ctx.author.bot and ctx.author.id != self.client.user.id:
                    await ctx.send('Bot aganist player??!, I want to see that')
            if user.id == ctx.author.id:
                await ctx.send('You can\'t play with yourself {}, find a friend'.format(user.mention))
                return False
            return True
        return False
    # checking whether this channel is allowed to receive game-related commands
    async def is_dis_game_channel(self,ctx):
        if str(ctx.guild.id) not in server_settings:
            await settings_defaults(ctx.guild.id)
            return True
        elif ctx.channel.id not in server_settings[str( ctx.guild.id )]["game_channel"] and len(server_settings[str( guild.id )]["game_channel"] ) > 0:
            # return random channel where game-related commands are allowed
            channel = self.client.get_channel( server_settings[str( ctx.guild.id )]["game_channel"][random.randint( 0,len(server_settings[str(ctx.guild.id )]["game_channel"] ) - 1 )] )
            if channel != None:
                await ctx.send("{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel.mention ) )
                return False
        return True

def setup(client):
    client.add_cog( Hangman( client ) )

class Game():
    def __init__(self,user):
        # Host
        self.user = user
        # Game message
        self.message = None
        self.rect_message = None

    # Create embed
    async def setup(self,channel):
        color = Utils.random_color()
        embed = discord.Embed(
            title = 'Hangman',
            color = color
        )
        embed.set_image(url='https://i.postimg.cc/CMX6bRPn/Hangman1.png')
        self.message = await channel.send(embed=embed)
        msg = self.message
        alphabet = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿']

        overflow_reactions = list()
        for letter in alphabet:
            # fetch message, so I have actual reactions
            msg_ = await Utils.fetch_message(channel,msg.id)
            if msg_ == None:
                self.abort()
            if len(msg_.reactions) < 20:
                await msg.add_reaction(letter)
            else:
                overflow_reactions.append(letter)

        embed = discord.Embed(
            title = 'Hangman part 2',
            description ='Since discord limits reactions to 20 per message, here are the remaining letters',
            color = color
        )

        self.rect_message = await channel.send(embed=embed)
        for letter in overflow_reactions:
             if len(self.rect_message.reactions) < 20:
                await self.rect_message.add_reaction(letter)

    async def abort(self):
        pass