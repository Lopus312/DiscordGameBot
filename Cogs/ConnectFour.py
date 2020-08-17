import discord, traceback, asyncio, random
import __main__ as main
from discord.ext import commands, tasks
from discord import User
from datetime import datetime
from __main__ import server_settings

c4_time = 30
c4_height = 6
c4_length = 7
embed_title = 'Connect Four'
embed_color = discord.Colour.from_rgb(225,94,235)

games = dict()
# 0=message, 1=time, 2=challenged, 3=challenger
timer_messages = [[],[],[],[]]
game = list()
surrender_list = [[],[]]
random.seed(datetime.now())

class ConnectFour(commands.Cog):

    def __init__(self,client):
        global game
        self.client = client
        self.update.start()
        for x in range( c4_height ):
            game.append( list() )
            for y in range( c4_length ):
                game[x].append( ":white_large_square:" )

    @commands.command()
    async def connectfour(self,ctx, user: User):
        await self.create_game(ctx,user)

    @commands.command()
    async def connect4(self, ctx, user: User):
        await self.create_game( ctx, user )

    @commands.command()
    async def c4(self, ctx, user: User):
        await self.create_game( ctx, user )

    @commands.command()
    async def cfour(self, ctx, user: User):
        await self.create_game( ctx, user )

    @commands.command()
    async def surrender(self,ctx):
        # checking whether this channel is allowed to receive game-related commands
        if str( ctx.guild.id ) not in server_settings:
            await main.settings_defaults( ctx.guild.id )
        if server_settings[str( ctx.guild.id )]["game_channel"] != str( ctx.channel.id ):
            channel = self.client.get_channel( server_settings[str( ctx.guild.id )]["game_channel"] )
            await ctx.send( "{} this channel can't be used for game-related command, try {}".format( ctx.author.mention,channel.mention ) )
            return

        if ctx.author.id in surrender_list[0]:
            await self.surrender_game(ctx.author.id)
        elif ctx.author.id in games[ctx.message.guild.id]:
            await ctx.send("{} Do you really want to surrender game of Connect four? type **%surrender** again if you are sure".format(ctx.author.mention))
            surrender_list[0].append(ctx.author.id)
            surrender_list[1].append(ctx.guild.id)
        else:
            await reaction.message.channel.send("{} Join a game first, before surrendering".format(ctx.author.mention))

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if user.id == self.client.user.id:
            return

        # Rejected game
        if reaction.emoji == '\U0001F6AB':
            if user.id not in timer_messages[2]:
                return
            ix = timer_messages[2].index( user.id )
            await reaction.message.channel.send('**{}** Has not accepted your challenge {}'.format( self.client.get_user(timer_messages[2][ix]).name, self.client.get_user(timer_messages[3][ix]).mention ))
            message = timer_messages[0][ix]
            timer_messages[0].remove( timer_messages[0][ix] )
            timer_messages[1].remove( timer_messages[1][ix] )
            timer_messages[2].remove( timer_messages[2][ix] )
            timer_messages[3].remove( timer_messages[3][ix] )
            await message.delete()

        # Accepted game - remove countdown messages and create game
        if reaction.emoji == '\U00002705':
            if user.id not in timer_messages[2]:
                return
            global games
            ix = timer_messages[2].index( user.id )
            message = timer_messages[0][ix]
            user_A = self.client.get_user(timer_messages[2][ix])
            user_B = self.client.get_user(timer_messages[3][ix])
            timer_messages[0].remove( timer_messages[0][ix] )
            timer_messages[1].remove( timer_messages[1][ix] )
            timer_messages[2].remove( timer_messages[2][ix] )
            timer_messages[3].remove( timer_messages[3][ix] )

            if reaction.message.guild.id in games:
                if user.id in games[reaction.message.guild.id]:
                    await ctx.send( "{} You are already in another game".format( user.mention ) )
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

            await message.delete()
            await game.prepare()

        # surrender game
        if reaction.emoji == '\U0000274C':
            if user.id not in games[reaction.message.guild.id]:
                return
            await reaction.message.channel.send("{} Do you really want to surrender game of Connect four? type **%surrender** if you are sure".format(user.mention))
            surrender_list[0].append(user.id)
            surrender_list[1].append(reaction.message.guild.id)

        # 1-7 moves
        if reaction.emoji == '1️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(1,user)
        if reaction.emoji == '2️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(2,user)
        if reaction.emoji == '3️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(3,user)
        if reaction.emoji == '4️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(4,user)
        if reaction.emoji == '5️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(5,user)
        if reaction.emoji == '6️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(6,user)
        if reaction.emoji == '7️⃣':
            if user.id not in games[reaction.message.guild.id]:
                return
            await games[user.guild.id][user.id].play(7,user)

    @tasks.loop( seconds=1.0 )
    async def update(self):
        #cooldown message
        if len(timer_messages[1])==0:
            return
        for x in range( len( timer_messages[1] ) ):
            try:
                message = timer_messages[0][x]
                message_str = message.content.replace( '{}s'.format(timer_messages[1][x]), '{}s'.format(timer_messages[1][x]-1) )
                await message.edit( content=message_str )
                if timer_messages[1][x] > 1:
                    timer_messages[1][x] -= 1
                else:
                    timer_messages[0].remove( timer_messages[0][x] )
                    timer_messages[1].remove( timer_messages[1][x] )
                    timer_messages[2].remove( timer_messages[2][x] )
                    timer_messages[3].remove( timer_messages[3][x] )

            except IndexError as e:
                print_date('IndexError in {}update{} function, will attempt to log to ./ConnectFour_Log.txt: {}'.format('\033[1;31;48m','\033[0;31;48m',e),error=True)
                write_log(traceback.format_exc())

    async def surrender_game(self,user_id):
        if user_id not in surrender_list[0]:
            return
        user_a = self.client.get_user( user_id )
        user_b = None
        guild = self.client.get_guild(surrender_list[1][surrender_list[0].index(user_id)])
        global games
        game = games[guild.id][user_a.id]

        for x in games[guild.id]:
            if game == games[guild.id][x] and x != user_id:
                user_b = self.client.get_user(x)

        if user_b == None:
            print_date("User_b not found after surrendering", error=True)
            return

        await game.msg.edit(content="{} surrendered 🏳️".format( user_a.mention ) )
        await game.msg.channel.send("{} surrendered a game againist {}".format(user_a.mention,user_b.mention))
        games[guild.id].pop(user_a.id)
        games[guild.id].pop(user_b.id)
        surrender_list[0].remove( user_id )
        surrender_list[1].remove( guild.id)
        print_date("{}({}) surrendered game to {}({}) ( {} )".format(user_a.name,user_a.mention,user_b.name,user_b.mention,games))

    async def create_game(self,ctx,user:User):
        global games,timer_messages

        # checking whether this channel is allowed to receive game-related commands
        if str(ctx.guild.id) not in server_settings:
            await main.settings_defaults(ctx.guild.id)

        if server_settings[str(ctx.guild.id)]["game_channel"]!=str(ctx.channel.id):
            channel = self.client.get_channel(server_settings[str(ctx.guild.id)]["game_channel"])
            await ctx.send( "{} this channel can't be used for game-related command, try {}".format( ctx.author.mention, channel.mention ) )
            return

        # if either of users is already in game, prevent starting another one
        if ctx.guild.id in games:
            if ctx.author.id in games[ctx.guild.id]:
                await ctx.send( ctx.author.mention + ' you are already in game, finish it before starting another one please.' )
                return
            elif user.id in games[ctx.guild.id]:
                await ctx.send( user.name + ' is already in game, wait for him to finish before challenging him' )
                return
            elif user.bot:
                await ctx.send('bruh, '+ctx.author.mention+' you can\'t challenge bot. you\'d be crushed and I can\'t allow you that fast defeat ')
                return
            elif  ctx.author.bot:
                await ctx.send('??? Bot aganist player?, I want to see that')
        if user.id == ctx.author.id:
            await ctx.send('You can\'t play with yourself {}, find a friend'.format(user.mention))
            return
        # creating cooldown message
        message = await ctx.send("{} you were challenged to a game of **Connect Four**! you have **{}s** to react to this message".format(user.mention,c4_time))
        timer_messages[0].append(message)
        timer_messages[1].append(c4_time)
        timer_messages[2].append(user.id)
        timer_messages[3].append(ctx.author.id)

        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0001F6AB")

def create_embed():
    global game
    embed = discord.Embed(
        title = embed_title,
        color = embed_color,
    )
    embed_desc = ""
    for x in range( len( game ) ):
        for y in range( len( game[x] ) ):
            embed_desc += str(game[x][y]).strip()
        embed_desc += '\n'
    embed.add_field(name='-', value=embed_desc)
    return embed

# writes log to .\ConnectFour_Log.txt
def write_log(string,date=True):
    try:
        f = open('ConnectFour_Log.txt','a+')
        if date:
            f.write(print_date(string,print_=False))
        else:
            f.write(string)
        f.close()
    except:
        print_date( 'Unexpected error: Could not write error to log file ({})'.format(string) ,error=True)

# adds date before string and prints it
# adds date before string and prints it
def print_date(string,print_=True,error=False):
    if error:
        str = '\033[0;31;48m'+datetime.now().strftime("%H:%M:%S")+" "+string+'\033[0;38;48m'
    else:
        str = datetime.now().strftime( "%H:%M:%S" ) + " " + string
    if print_:
        print(str)
    return str

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

        self.last_playing_user = self.playing_user
        self.playing_user = None

        game_field = self.game_field
        move = move-1
        # placing circle
        game_length = len(game_field)-1
        for x in range(0,len(game_field)):
            if game_field[game_length-x][move].strip()==':white_large_square:':
                if self.last_playing_user == self.user_A.name:
                    game_field[game_length-x][move]=':yellow_circle:'
                else:
                    game_field[game_length - x][move] = ':red_circle:'
                break

        await self.check_for_win()

        # creating embed description from game_field
        embed_desc = ""
        for x in range(len(game_field)):
            for y in range(len(game_field[x])):
                embed_desc += str(game_field[x][y]).strip()
            embed_desc += '\n'
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
                            await self.win( self.user_A if scanned_players == 1 else self.user_B )
                            return
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
                                        await self.win(self.user_A if scanned_players == 1 else self.user_B)
                                        return
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
                                    await self.win( self.user_A if scanned_players == 1 else self.user_B )
                                    return
                            else:
                                count_diagonal_to_right = 0
                            # Diagonal right to left <--------
                            if next_y_l != -1 and game_field[next_x][next_y_l] == player_emote:
                                count_diagonal_to_left += 1
                                next_y_l = next_y_l - 1 if next_y_l - 1 >= 0 else -1
                                if count_diagonal_to_left >= 4:
                                    await self.win( self.user_A if scanned_players == 1 else self.user_B )
                                    return
                            else:
                                count_diagonal_to_left = 0
                    else:
                        count_horizontal = 0
                    count_vertical = 0
                count_horizontal = 0
            scanned_players += 1

    async def win(self,user):
        global games
        #if user is not in this game, he can't win
        if user.id != self.user_A.id and user.id != self.user_B.id:
            write_log(print_date("{}({}) is trying to win in a game he has not entered: games:{}".format(user,user.id,games), error=True),date=False)
            return

        user_lost = self.user_A if user.id == self.user_B.id else self.user_B
        guild = self.msg.guild

        await self.msg.edit(content="{} won 🎉".format( user.mention ) )
        await self.msg.channel.send("{} won against {} in a game of Connect Four".format(user.mention,user_lost.mention))

        #removing user from games
        try:
            games[guild.id].pop(user.id)
            games[guild.id].pop(user_lost.id)
        except:
            print_date("Unexpected error inside win method, check log for more info",error=True)
            write_log( traceback.format_exc() )

        print_date("{}({}) won game of Connect Four against {}({}) games:{}".format(user.name,user.mention,user_lost.name,user_lost.mention,games))
