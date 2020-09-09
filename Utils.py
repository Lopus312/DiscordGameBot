from datetime import datetime
import discord, traceback
from discord.ext import commands



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

def setup(client):
    client.add_cog( Utils( client ) )