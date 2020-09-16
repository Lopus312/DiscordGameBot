import discord, Utils
from discord.ext import commands
from datetime import datetime
from __main__ import settings_defaults, server_settings

games = dict()
waiting_room = [[],[],[]]

class Hangman(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.waiting_room = waiting_room

    async def hangman(self,ctx):
        # Create Game class
        gm = Game(ctx.author)

        await gm.setup(ctx.channel)
        gm.members.append(str(ctx.author.id))

        # Save Game
        if ctx.guild.id in games:
            games[ctx.guild.id]['Game'] = gm
        else:
            games[ctx.guild.id] = dict()
            games[ctx.guild.id]['Game'] = gm

    async def join(self,ctx):
        if str(ctx.author.id) not in games[ctx.guild.id]['Game'].members:
            games[ctx.guild.id]['Game'].members.append(str(ctx.author.id))
        else:
            await ctx.send(f'{ctx.author.mention} you are already in game')

    async def guess(self,ctx,arg):
        if ctx.guild.id in games:
            await games[ctx.guild.id]['Game'].guess(arg)

    @commands.Cog.listener()
    async def on_message(self,message):
        if type(message.channel) == discord.DMChannel and message.author.id != self.client.user.id:
            if message.author.id in waiting_room[0]:
                game = waiting_room[1][waiting_room[0].index(message.author.id)]
                await game.set_word(message.content)

                await message.channel.send(embed=Utils.get_embed(title='Word recorded',desc='Link will only work on desktop',name='Link',value=f'[Take me back to hangman]({game.link})'))
                self.waiting_room_remove(waiting_room[1].index(game))

    def waiting_room_remove(self,ix):
        try:
            waiting_room[0].pop(ix)
            waiting_room[1].pop(ix)
            waiting_room[2].pop(ix)
        except ValueError as e:
            Utils.print_date('ValueError: {} in hangman.waiting_room_remove (waiting_room:{} user_id:{})'.format(e,waiting_room,user_id),errlog=True)
            return

    async def can_i_create_invite(self,ctx):
        if await self.is_dis_game_channel(ctx):
            # Checking if game can start
            if ctx.guild.id in games:
                if user.bot:
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
        self.word = None
        self.embed = None
        self.members = list()

    # Create embed
    async def setup(self,channel):

        if self.user.dm_channel == None:
            await self.user.create_dm()
        await self.user.dm_channel.send('Send me a word which you would like to use in hangman game')
        color = Utils.random_color()
        embed = discord.Embed(
            title = 'Hangman',
            color = color,
            timestamp=datetime.now()
        )
        embed.description = 'Waiting to receive word from host...'
        self.message = await channel.send(embed=embed)
        self.link = 'https://discordapp.com/channels/{}/{}/{}'.format(self.message.guild.id,self.message.channel.id,self.message.id)

        waiting_room[0].append(self.user.id)
        waiting_room[1].append(self)
        waiting_room[2].append(embed.timestamp)

    async def set_word(self,word):
        self.word = word.upper()

        # for some reason if you put multiple spaces in embed desc. discord removes all of them except one
        # so to make bigger space in-between words i need to use unicode character for no-break space
        space = '\U000000A0\U000000A0\U000000A0\U000000A0'
        string = ''
        for letter in self.word.strip():
            if letter == ' ':
                string+=space
            else:
                # cuz '_' is also used in markdown as underline, you need to place '\' in front of it
                string +=' \_'

        color = Utils.random_color()
        embed = discord.Embed(
            title = 'Hangman',
            color = color,
            timestamp=datetime.now()
        )
        embed.description = string

        f = discord.File("Cogs/Hangman/Hangman1.png", filename="Hangman1.png")
        embed.set_image(url="attachment://Hangman1.png")

        #embed.set_image(url='https://i.postimg.cc/CMX6bRPn/Hangman1.png')
        embed.add_field(name='Players: ',value=self.user.name)
        await self.message.channel.send(file=f, embed=embed)
        self.embed = embed
        #await self.message.edit(embed=embed)

    async def guess(self,letter_):
        # guessed letters are lowercase
        letter = str(letter_).upper()

        if type(letter) == str:

            self.word=self.word.replace(letter[0],letter[0].lower())
            #print(self.word)

            space = '\U000000A0\U000000A0\U000000A0\U000000A0'
            string = ''
            # if letter is lowercase, show the letter else show underscore
            for letter in self.word:
                if letter == ' ':
                    string+=space
                else:
                    if letter.islower():
                        string+=f' {letter}'
                    else:
                        string +=' \_'

            self.embed.description = string.upper()

            await self.message.edit(embed=self.embed)
            self.embed.set_field_at(0,name='Players:',value=' '.join(self.members))

            if self.is_end():
                await self.message.channel.send('u good, u won')

    def is_end(self):
        for letter in self.word:
            if letter.isupper():
                return False
        return True