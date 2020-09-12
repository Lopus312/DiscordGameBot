from datetime import datetime
import discord, traceback,random
from discord.ext import commands


random.seed(datetime.now())

class Utils(commands.Cog):
    pass

def print_date(string: str, print_=True, error=False, warning=False, log=False):
    time = datetime.now().strftime( "%H:%M:%S" )
    date = datetime.now().strftime( "%d.%m. %H:%M:%S" )

    if log:
        try:
            f = open( 'DiscordBot2_log.txt', 'a+' )
            if error:
                f.write( '\n{} {}\nTraceback:{}'.format( date, string, traceback.format_exc() ) )
            else:
                f.write( '\n{} {}'.format( date, string ) )
            f.close()
        except:
            print_date( 'Unexpected error: Could not write error to log file ({})'.format( string ), error=True )
    if error:
        str_ = '\033[0;31;48m{} {}\033[0;38;48m'.format( time, string )
    elif warning:
        str_ = '\033[0;93;48m{} {}\033[0;38;48m'.format( time, string )
    else:
        str_ = '{} {}'.format( time, string )
    if print_:
        print( str_ )
    return str_

async def send_embed(channel,title="",desc="",color = None,name="",value="",text=""):
    embed = discord.Embed(
        title=title,
        description=desc,
        color = color if color != None else discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)),
    )
    embed.add_field(name=name,value=value,)
    await channel.send(text,embed=embed)

def random_color():
    return discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))

async def fetch_message(channel,msg_id):
    try:
        msg_= await channel.fetch_message(msg_id)
        return msg_
    except discord.NotFound:
        Utils.print_date('discord.NotFound exception: in Utils.fetch_message channel:{}'.format(channel),warning=True)
        return None
    except discord.Forbidden:
        Utils.print_date('discord.Forbidden exception: in Utils.fetch_message, Bot doesn\'t have permissions to get a message'.format(channel),warning=True)
        return None
    except discord.HTTPException as e:
        Utils.print_date('discord.HTTPException: {} in Utils.fetch_message, channel: {}'.format(e,channel),log=True,error=True)
        return None


def setup(client):
    client.add_cog( Utils( client ) )