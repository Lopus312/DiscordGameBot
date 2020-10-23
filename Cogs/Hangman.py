import discord, Utils, random
from discord.ext import commands
from datetime import datetime
from __main__ import settings_defaults, server_settings

games = dict()
# Waiting for dm message
waiting_room = [[],[],[]]

class Hangman(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.waiting_room = waiting_room

    async def hangman(self,ctx):

        if ctx.guild.id in games:
            for game in games[ctx.guild.id]['Game']:
                if ctx.author.id == game.user.id or str(ctx.author.id) in game.members[0]:
                    ctx.send('You have already created or joined a game, type `%findmygame` to find it')
                    return

        # Create Game class
        gm = Game(ctx.author)
        await gm.setup(ctx.channel)
        gm.members[0].append(str(ctx.author.id))
        gm.members[1].append(str(ctx.author.name))

        # Save Game into games dict
        if ctx.guild.id not in games:
            games[ctx.guild.id] = dict()
        if 'Game' not in games[ctx.guild.id]:
            temp = dict()
            temp['Game'] = [gm]
            games[ctx.guild.id] = dict()
            games[ctx.guild.id] = temp
        else:
            games[ctx.guild.id]['Game'].append(gm)

    # join hangman game, args[0] can be id of a game
    async def join(self,ctx,args):
        # default id of game
        ix = 0
        # try to get id from args
        if len(args)>0:
            try:
                ix = int(args[0])
            except SyntaxError:
                pass
        if ix<0:
            await ctx.send(f'{ctx.author.mention} game id cannot be negative! You specified **{ix}** as id')
            return
        # find game and try to join player
        if ix > 0 :
            for game in games[ctx.guild.id]['Game']:
                if game != None and game.id == ix:
                    game.join(ctx.author)
                    return
            await ctx.send(f'{ctx.author.mention} specified id is not assigned to any game')
            return
        # join first available game
        for game in games[ctx.guild.id]['Game']:
                if ctx.author.id != game.user.id and str(ctx.author.id) not in game.members[0]:
                    await game.join(ctx.author)
                    return
        await ctx.send(f'{ctx.author.mention} Can\'t find any game for you to join')

    async def guess(self,ctx,arg):

        if arg.lower() == 'cancel':
             for game in games[ctx.guild.id]['Game']:
                if ctx.author.id == game.user.id or str(ctx.author.id) in game.members[0]:
                    await game.delete()
                    await ctx.send('Game was deleted')

        elif ctx.guild.id in games:
            for game in games[ctx.guild.id]['Game']:
                if str(ctx.author.id) in game.members[0]:
                    await game.guess(arg)

    # Dm's listener
    @commands.Cog.listener()
    async def on_message(self,message):
        if type(message.channel) == discord.DMChannel and message.author.id != self.client.user.id:
            if message.author.id in waiting_room[0]:
                game = waiting_room[1][waiting_room[0].index(message.author.id)]
                await game.set_word(message.content)
                await message.channel.send(embed=Utils.get_embed(title=f'Message "{message.content}" recorded',desc='Following link will only work on desktop',name='Link',value=f'[Take me back to hangman]({game.link})'))
                self.waiting_room_remove(waiting_room[1].index(game))

    def waiting_room_remove(self,ix):
        try:
            waiting_room[0].pop(ix)
            waiting_room[1].pop(ix)
            waiting_room[2].pop(ix)
        except ValueError as e:
            Utils.print_date('ValueError: {} in hangman.waiting_room_remove (waiting_room:{})'.format(e,waiting_room),errlog=True)
            return

    async def can_i_create_invite(self,ctx,user):
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
        self.lifes = 11
        self.lifes_total = 11
        self.id = -1
        # 0 = id, 1 = name
        self.members = [[],[]]

    # Create embed
    async def setup(self,channel):

        # Create id
        try:
            if str(channel.guild.id) in games:
                id = games[str(channel.guild.id)]['Games'].index(self)
                id_set = False
                try:
                    while id_set:
                        temp_id = id
                        for game in games[str(channel.guild.id)]['Games']:
                            if id == game.id:
                                id+=1
                                continue
                        if id == temp_id:
                            id_set=True
                            self.id = id
                except RuntimeError as e:
                    Utils.print_date(f'Hangman error while creating id: RuntimeError:{e}',errlog=True)
                    self.delete()
                    return
            else:
                self.id = 0
        except ValueError as e:
            Utils.print_date(f'Hangman: Could not create game id (two games created at the same time probably): {e}',warning=True)
            self.delete()
            return

        if self.id == -1:
            await channel.send(f'Could not create id for Hangman game, terminating...')
            self.delete()
            return

        color = Utils.random_color()
        embed = discord.Embed(
            title = 'Hangman',
            color = color,
            timestamp=datetime.now()
        )
        embed.description = 'Waiting to receive word from host...'
        self.message = await channel.send(embed=embed)
        self.link = 'https://discordapp.com/channels/{}/{}/{}'.format(self.message.guild.id,self.message.channel.id,self.message.id)

        # Wait for dm message to be sent
        waiting_room[0].append(self.user.id)
        waiting_room[1].append(self)
        waiting_room[2].append(embed.timestamp)
        # Send dm message
        if self.user.dm_channel == None:
            await self.user.create_dm()
        await self.user.dm_channel.send(f'Next message you send me will be recorded and used for hangman game in **{self.message.guild.name}** or *type cancel to delete the game*')

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
            title = f'Hangman [{self.id}]',
            color = color,
            timestamp=datetime.now()
        )
        embed.description = string
        num = self.lifes_total-self.lifes
        f = discord.File(f"Cogs/Hangman/Hangman{num}.png", filename=f"Hangman{num}.png")
        embed.set_image(url=f"attachment://Hangman{num}.png")

        #embed.set_image(url='https://i.postimg.cc/CMX6bRPn/Hangman1.png')
        embed.add_field(name='Host: ',value=self.user.name)
        embed.add_field(name='Players: ',value=", ".join(self.members[1]))
        await self.message.delete()
        self.message = await self.message.channel.send(file=f, embed=embed)
        self.embed = embed
        #await self.message.edit(embed=embed)

    async def guess(self,letter_):
        # guessed letters are lowercase
        letter = str(letter_).upper()

        if letter in self.word:
            self.word=self.word.replace(letter[0],letter[0].lower())
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
            else :
                self.lifes-=1
            self.embed.description = string.upper()

            await self.refresh()

            if self.is_end():
                await self.message.channel.send('u good, u won')

    async def join(self,user):
        if str(user.id) not in self.members[0]:
            self.members[0].append(str(user.id))
        if str(user.name) not in self.members[1]:
            self.members[1].append(str(user.name))
        await self.refresh()

    async def refresh(self):
        self.embed.set_field_at(1,name='Host:',value=str(self.user.name))
        self.embed.set_field_at(1,name='Players:',value=', '.join(self.members[1]))
        await self.message.edit(embed=self.embed)

    def is_end(self):
        for letter in self.word:
            if letter.isupper():
                return False
        return True

    async def loss(self):
        await self.message.channel.send('u lose')

    def delete(self):
        try:
            i = games[self.message.guild.id]['Game'].index(self)
        except ValueError:
            Utils.print_date(f'Hangman: trying to delete game from dict that does not exist games:{games} server:{"Not Available" if self.message == None else self.message.guild} id:{self.id}',warning=True)
        games[self.message.guild.id]['Game'].pop(i)