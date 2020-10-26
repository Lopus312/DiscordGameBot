import discord, traceback, asyncio, random
import __main__ as main
from discord.ext import commands, tasks
from discord import User
from datetime import datetime
from __main__ import server_settings
import Utils
from Cogs.Classes.Stats import Stats
from Cogs.GameManager import GameManager

c4_time = 30
c4_height = 6
c4_length = 7
embed_title = 'Connect Four'
embed_color = discord.Colour.from_rgb(225,94,235)

games = dict()

game = list()
surrender_list = [[],[]]
random.seed(datetime.now())

class ConnectFour(commands.Cog):

    def __init__(self,client):
        global game
        self.client = client
        self.timer_messages = GameManager.get_invite_messages(GameManager)
        self.games = games
        self.cd_time = c4_time
        for x in range( c4_height ):
            game.append( list() )
            for y in range( c4_length ):
                game[x].append( ":white_large_square:" )

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user.id == self.client.user.id:
            return

        # Rejected game
        if reaction.emoji == '\U0001F6AB':
            invite_messages = GameManager.get_invite_messages(GameManager)
            if user.id not in invite_messages[2]:
                return
            ix = invite_messages[2].index( user.id )
            await reaction.message.channel.send('**{}** Has not accepted your challenge {}'.format( self.client.get_user(invite_messages[2][ix]).name, self.client.get_user(invite_messages[3][ix]).mention ))
            await GameManager.invite_remove(GameManager,user.id)
            return

        # Accepted game - remove countdown messages and create game
        if reaction.emoji == '\U00002705':
            invite_messages = GameManager.get_invite_messages(GameManager)
            if user.id not in invite_messages[2]:
                return
            global games
            # delete countdown message
            ix = invite_messages[2].index( user.id )
            message = invite_messages[0][ix]
            user_A = self.client.get_user(invite_messages[2][ix])
            user_B = self.client.get_user(invite_messages[3][ix])

            if reaction.message.guild.id in games:
                if reaction.message.guild.id in games:
                    if user.id in games[reaction.message.guild.id]:
                        await reaction.message.channel.send( "{} You are already in another game".format( user.mention ) )
                        return

            #create embed, game and add to games dict
            g_embed = create_embed()
            g_message = await reaction.message.channel.send(embed = g_embed)
            game = Game(user_A,user_B,g_message,g_embed)
            if message.guild.id in games:
                games_user_a = dict()
                games_user_b = dict()
                games_user_a[user_A.id] = game
                games_user_b[user_B.id] = game
                games[message.guild.id].update( games_user_a)
                games[message.guild.id].update( games_user_b)
            else:
                games_user_a = dict()
                games_user_b = dict()
                games_user_a[user_A.id] = game
                games_user_b[user_B.id] = game
                games[message.guild.id] = games_user_a
                games[message.guild.id].update(games_user_b)

            await GameManager.invite_remove(GameManager,user.id)
            await game.prepare()
            return

        # surrender game
        if reaction.emoji == '\U0000274C':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                if user.id not in surrender_list[0]:
                    await reaction.message.channel.send("{} Do you really want to surrender game of Connect four? type **%surrender** if you are sure".format(user.mention))
                    surrender_list[0].append(user.id)
                    surrender_list[1].append(reaction.message.guild.id)
                return

        # 1-7 moves
        if reaction.emoji == '1️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(1,user)
                await reaction.remove( user )
        if reaction.emoji == '2️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(2,user)
                await reaction.remove( user )
        if reaction.emoji == '3️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(3,user)
                await reaction.remove( user )
        if reaction.emoji == '4️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(4,user)
                await reaction.remove( user )
        if reaction.emoji == '5️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(5,user)
                await reaction.remove( user )
        if reaction.emoji == '6️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(6,user)
                await reaction.remove( user )
        if reaction.emoji == '7️⃣':
            if reaction.message.guild.id in games:
                if user.id not in games[reaction.message.guild.id]:
                    return
                await games[user.guild.id][user.id].play(7,user)
                await reaction.remove( user )

    # Checking if user can surrender or not
    async def surrender(self,ctx):
        # Channel checking...
        if str(ctx.guild.id) not in server_settings:
            await main.settings_defaults(ctx.guild.id)
        elif ctx.channel.id not in server_settings[str(ctx.guild.id)]["game_channel"] and len(server_settings[str(ctx.guild.id)]["game_channel"])>0:
            # return random channel where game-related commands are allowed
            channel = self.client.get_channel(server_settings[str(ctx.guild.id)]["game_channel"][random.randint(0,len(server_settings[str(ctx.guild.id)]["game_channel"])-1)])
            if channel != None:
                await ctx.send( "{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel.mention ) )
                return

        # if author already tried to surrender, surrender instantly if not, send surrender message and add him to he list
        if ctx.author.id in surrender_list[0]:
            await self.surrender_game(ctx.author.id)
        elif ctx.message.guild.id in games and ctx.author.id in games[ctx.message.guild.id]:
            await ctx.send("{} Do you really want to surrender game of Connect four? type **%surrender** again if you are sure".format(ctx.author.mention))
            surrender_list[0].append(ctx.author.id)
            surrender_list[1].append(ctx.guild.id)
            return
        else:
            await ctx.send("{} Join a game first, before surrendering".format(ctx.author.mention))
            return

    async def surrender_game(self,user_id):
        if user_id not in surrender_list[0]:
            return
        user = self.client.get_user( user_id )
        guild_id = surrender_list[1][surrender_list[0].index(user_id)]

        global games
        await games[guild_id][user.id].surrender(user)

    async def can_i_create_invite(self,ctx,user):
        # If author did not mention user
        if user == None:
            await ctx.send("You have to mention someone who you want to play with. \nExample: **%c4 {}**".format(ctx.author.mention))
            return False
        # checking whether this channel is allowed to receive game-related commands
        if str(ctx.guild.id) not in server_settings:
            await main.settings_defaults(ctx.guild.id)
        elif ctx.channel.id not in server_settings[str( ctx.guild.id )]["game_channel"] and len(server_settings[str( ctx.guild.id )]["game_channel"] ) > 0:
            # return random channel where game-related commands are allowed
            channel = self.client.get_channel( server_settings[str( ctx.guild.id )]["game_channel"][random.randint( 0,len(server_settings[str(ctx.guild.id )]["game_channel"] ) - 1 )] )
            if channel != None:
                await ctx.send("{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel.mention ) )
                return False
        # Checking if game can start
        if ctx.guild.id in games:
            if ctx.author.id in games[ctx.guild.id]:
                await ctx.send( ctx.author.mention + ' you are already in game, finish it before starting another one please. If you lost your game type `%findmygame`' )
                return False
            elif user.id in games[ctx.guild.id]:
                await ctx.send( user.name + ' is already in game, wait for him to finish before challenging him' )
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

def create_embed():
    global game
    embed = discord.Embed(
        title = embed_title,
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)),
    )
    embed_desc = ""
    for x in range( len( game ) ):
        for y in range( len( game[x] ) ):
            embed_desc += str(game[x][y]).strip()
        embed_desc += '\n'
    embed_desc+=':one::two::three::four::five::six::seven:'
    embed.add_field(name='-', value=embed_desc)
    return embed

def setup(client):
    client.add_cog( ConnectFour( client ) )

class Game:
    def __init__(self,user_A:User,user_B:User,message,embed):
        self.user_A = user_A
        self.user_B = user_B
        self.playing_user = None
        self.last_playing_user = None
        self.msg = message
        self.embed = embed
        self.game_field = list()
        self.winning_four = list()

    async def prepare(self):

        # prepare field
        for x in range( c4_height ):
            self.game_field.append( list() )
            for y in range( c4_length ):
                self.game_field[x].append( ":white_large_square:" )
        # add reactions
        msg = self.msg
        embed = self.embed
        await msg.edit(embed=self.embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣')
        await msg.add_reaction('3️⃣')
        await msg.add_reaction('4️⃣')
        await msg.add_reaction('5️⃣')
        await msg.add_reaction('6️⃣')
        await msg.add_reaction('7️⃣')
        await msg.add_reaction('\U0000274C')
        #send messages
        self.playing_user = self.user_A.name if random.randint(0,100) <= 50 else self.user_B.name
        icon = ":yellow_circle:" if self.playing_user == self.user_A.name else ":red_circle:"
        embed.set_field_at(0,name="{}{}'s turn".format(icon,self.playing_user),value=embed.fields[0].value)
        await msg.edit(embed=embed)

    async def play(self,move,user):
        if user.name != self.playing_user:
            return

        game_field = self.game_field
        move = move-1
        move_ = None
        game_length = len( game_field ) - 1

        # replacing colored squares
        for x in range(0,len(game_field)):
            for y in range(len(game_field[x])):
                if game_field[x][y]==':yellow_square:':
                    game_field[x][y]=':yellow_circle:'
                elif game_field[x][y]==':red_square:':
                    game_field[x][y] = ':red_circle:'
        # placing circle
        for x in range(0,len(game_field)):
            if game_field[game_length-x][move].strip()==':white_large_square:':
                if self.playing_user == self.user_A.name:
                    game_field[game_length-x][move]=':yellow_circle:'
                    move_ = [game_length-x,move]
                else:
                    game_field[game_length - x][move] = ':red_circle:'
                    move_ = [game_length-x,move]
                break

        if move_ == None:
            return

        if await self.check_for_win():
            return

        if self.playing_user == self.user_A.name:
            game_field[move_[0]][move_[1]] = ':yellow_square:'
        else:
            game_field[move_[0]][move_[1]] = ':red_square:'

        self.last_playing_user = self.playing_user
        self.playing_user = None

        # creating embed description from game_field
        embed_desc = ""
        for x in range(len(game_field)):
            for y in range(len(game_field[x])):
                embed_desc += str(game_field[x][y]).strip()
            embed_desc += '\n'
        embed_desc += ':one::two::three::four::five::six::seven:'
        # editing message
        self.game_field = game_field
        icon = ":yellow_circle:" if self.last_playing_user != self.user_A.name else ":red_circle:"
        self.playing_user = self.user_A.name if self.last_playing_user == self.user_B.name else self.user_B.name
        self.embed.set_field_at(0,name="{}{}'s turn".format(icon,self.playing_user),value=embed_desc)
        await self.msg.edit(embed=self.embed)

    async def check_for_win(self):
        game_field = self.game_field
        player_count = 2
        scanned_players = 0
        players = ["red", "yellow"]

        while scanned_players < player_count:
            player_emote = ":{}_circle:".format( players[scanned_players] )
            count_horizontal = 0
            count_vertical = 0

            for x in range( len( game_field ) ):
                for y in range( len( game_field[x] ) ):
                    if game_field[x][y].strip() == player_emote:
                        # Horizontal
                        count_horizontal += 1
                        if count_horizontal == 4:
                            self.winning_four = [[x,x,x,x],[y,y-1,y-2,y-3]]
                            await self.win( self.user_A if scanned_players == 1 else self.user_B )
                            return True
                        # Vertical
                        count_vertical += 1
                        vert_next = x + 1 if x + 1 < len( game_field ) else -1
                        if vert_next != -1:
                            for z in range( 0, len( game_field ) ):
                                if vert_next != -1 and game_field[vert_next][y] == player_emote:
                                    vert_next = vert_next + 1 if vert_next + 1 < len( game_field ) else -1
                                    count_vertical += 1
                                    # Vertical win
                                    if count_vertical == 4:
                                        self.winning_four = [[x,x+1,x+2,x+3],[y,y,y,y]]
                                        await self.win(self.user_A if scanned_players == 1 else self.user_B)
                                        return True
                        # Diagonal
                        count_diagonal_to_right = 1
                        count_diagonal_to_left = 1
                        next_y_r = y + 1 if y + 1 < len( game_field[x] ) else -1
                        next_y_l = y - 1 if y - 1 >= 0 else -1
                        for z in range( 0, 4 ):
                            if x+z+1 < len(game_field):
                                next_x = x+z+1
                            else:
                                break
                            # Diagonal left to right -------->
                            if next_y_r != -1 and game_field[next_x][next_y_r] == player_emote:
                                count_diagonal_to_right += 1
                                next_y_r = next_y_r + 1 if next_y_r + 1 < len( game_field[x] ) else -1
                                if count_diagonal_to_right == 4:
                                    self.winning_four = [[x,x+1,x+2,x+3],[y,y+1,y+2,y+3]]
                                    await self.win( self.user_A if scanned_players == 1 else self.user_B )
                                    return True
                            else:
                                count_diagonal_to_right = 0
                            # Diagonal right to left <--------
                            if next_y_l != -1 and game_field[next_x][next_y_l] == player_emote:
                                count_diagonal_to_left += 1
                                next_y_l = next_y_l - 1 if next_y_l - 1 >= 0 else -1
                                if count_diagonal_to_left >= 4:
                                    self.winning_four = [[x,x+1,x+2,x+3],[y,y-1,y-2,y-3]]
                                    await self.win( self.user_A if scanned_players == 1 else self.user_B )
                                    return True
                            else:
                                count_diagonal_to_left = 0
                    else:
                        count_horizontal = 0
                    count_vertical = 0
                count_horizontal = 0
            scanned_players += 1

        # check if there are turns available
        for x in range( len( game_field ) ):
            for y in range( len( game_field[x] ) ):
                if game_field[x][y].strip() == ":white_large_square:":
                    return
        await self.draw()
        return True

    async def draw(self):
        guild = self.msg.guild

        game_field = self.game_field
        embed_desc = ""
        for x in range(len(game_field)):
            for y in range(len(game_field[x])):
                embed_desc += str(game_field[x][y]).strip()
            embed_desc += '\n'

        self.embed.set_field_at(0,name=":game_die: {} drew against {}".format(self.user_A.name, self.user_B.name ),value=embed_desc)
        await self.msg.edit( content=":game_die: {} drew against {}".format( self.user_A.mention, self.user_B.mention ),embed=self.embed )
        await self.msg.channel.send("{} and {} drew game of Connect Four".format(  self.user_A.mention,  self.user_B.mention ) )
        await self.remove_reactions()

        Stats.draw( Stats, guild, [self.user_A,self.user_B])

        try:
            games[guild.id].pop(self.user_A.id)
            games[guild.id].pop(self.user_B.id)
        except:
            Utils.print_date("ConnectFour: Unexpected error inside draw method, check log for more info",error=True,log=True)

    async def win(self,user):
        global games
        #if user is not in this game, he can't win
        if user.id != self.user_A.id and user.id != self.user_B.id:
            Utils.print_date("ConnectFour: {}({}) is trying to win in a game he has not entered: games:{}".format(user,user.id,games), error=True,log=True)
            return

        game_field = self.game_field
        user_lost = self.user_A if user.id == self.user_B.id else self.user_B
        guild = self.msg.guild

        # highlight winning four
        if self.winning_four != None:
            for i in range(0,4):
                x = self.winning_four[0][i]
                y = self.winning_four[1][i]
                print(f'x: {x} y: {y} gf:"{game_field[x][y]}"')
                if game_field[x][y] == ':red_circle:':
                    game_field[x][y] = ':red_square:'
                elif game_field[x][y] == ':yellow_circle:':
                    game_field[x][y] = ':yellow_square:'

        # Create embed description
        embed_desc = ""
        for x in range(len(game_field)):
            for y in range(len(game_field[x])):
                embed_desc += str(game_field[x][y]).strip()
            embed_desc += '\n'

        self.embed.set_field_at(0,name="{} won 🎉".format( user.name ),value=embed_desc)

        await self.msg.edit(content="{} won 🎉".format( user.mention ),embed=self.embed)
        await self.msg.channel.send("{} won against {} in a game of Connect Four".format(user.mention,user_lost.mention))
        await self.remove_reactions()

        Stats.win(Stats,guild,user,user_lost)

        #removing user from games
        try:
            games[guild.id].pop(user.id)
            games[guild.id].pop(user_lost.id)
        except:
            Utils.print_date("ConnectFour: Unexpected error inside win method, check log for more info",error=True,log=True)

    async def surrender(self,user):
        global games

        if user.id != self.user_A.id and user.id != self.user_B.id:
            Utils.print_date("User tried to surrender game he is not member of (user:{})".format(user),warning=True,log=True)
            return

        user_a = self.user_A if user.id == self.user_A.id else self.user_B      # What is this doing here???
        user_b = self.user_B if user_a.id == self.user_A.id else self.user_A
        guild = self.msg.guild
        game = games[guild.id][user_a.id]

        await self.remove_reactions()
        Stats.surrender(Stats,guild, user_a)

        game_field = self.game_field
        embed_desc = ""
        for x in range(len(game_field)):
            for y in range(len(game_field[x])):
                embed_desc += str(game_field[x][y]).strip()
            embed_desc += '\n'

        self.embed.set_field_at(0,name="{} surrendered 🏳️".format( user_a.name ),value=embed_desc)
        await game.msg.edit(content="{} surrendered 🏳️".format( user_a.mention ),embed=self.embed )
        await game.msg.channel.send("{} surrendered a game againist {}".format(user_a.mention,user_b.mention))

        await game.remove_reactions()
        games[guild.id].pop(user_a.id)
        games[guild.id].pop(user_b.id)
        surrender_list[0].remove( user.id )
        surrender_list[1].remove( guild.id)
        Utils.print_date("ConnectFour: {}({}) surrendered game to {}({}) ( {} )".format(user_a.name,user_a.mention,user_b.name,user_b.mention,games))

    async def remove_reactions(self):
        msg = await Utils.fetch_message(self.msg.channel,self.msg.id)

        for reaction in msg.reactions:
            await reaction.clear()