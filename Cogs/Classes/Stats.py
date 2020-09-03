from discord import User, Member
import __main__ as main

stat_dict = dict()

class Stats():

    def surrender(self, guild, user):
        global stat_dict
        user_list = self.toList( self, user )
        for user_ in user_list:
            self.createDefaults( self, guild, user_ )
            stat_dict[str( guild.id )][str( user_.id )]["surrenders"] += 1

    def draw(self, guild, user):
        global stat_dict
        user_list = self.toList( self, user )

        if user_list == None or user2_list == None:
            main.print_date( "UnhandledType Error: StatEdit.draw(), user_list({}) is not list or Member or User".format(
                type( user_list ), error=True, log=True ) )
            return

        for user_ in user_list:
            self.createDefaults( self, guild, user_ )
            stat_dict[str( guild.id )][str( user_.id )]["draws"] += 1
            stat_dict[str( guild.id )][str( user_.id )]["games"] += 1

    # user = user who won, user_lost = user who lost (both can be lists), chk_loss = also run loss()
    def win(self, guild, user, user_lost, chk_loss=True):
        global stat_dict
        user_list = self.toList(self, user )
        user_lost_list = self.toList(self, user_lost )

        # User variable type check
        if user_list == None or user_lost_list == None:
            main.print_date( "UnhandledType Error: StatEdit.win(), user_list({}) or user_lost_list({}) is not list or Member or User".format( type( user_list ), type( user_lost_list ) ), error=True, log=True )
            return

        # preventing user from winning against himself
        for user_w in user_list:
            for user_l in user_lost_list:
                if user_w.id == user_l.id:
                    main.print_date( "{}({}) tried to win against himself, removing him from lists...".format( user_w.name, user_w.id ) )
                    user_list.remove( user_w )
                    user_lost_list.remove( user_l )
                    if len( user_list ) == 0:
                        return
        # Increasing wins and games
        for user_ in user_list:
            self.createDefaults(self, guild, user_ )
            stat_dict[str( guild.id )][str( user_.id )]["wins"] += 1
            stat_dict[str( guild.id )][str( user_.id )]["games"] += 1

            for lost_user in user_lost_list:
                # if user won against user_lost for the first time, add him to "Unique_wins"
                if lost_user.id not in stat_dict[str( guild.id )][str( user_.id )]["unique_wins"]:
                    stat_dict[str( guild.id )][str( user_.id )]["unique_wins"].append( lost_user.id )

        if chk_loss:
            self.loss(self, guild, user_lost_list, user_list, chk_win=False )

    # almost the same as StatEdit.win()
    def loss(self, guild, user, user_won, chk_win=True):
        global stat_dict
        user_list = self.toList(self, user )
        user_won_list = self.toList(self, user_won )

        if user_list == None or user_won_list == None:
            main.print_date("UnhandledType Error: StatEdit.loss(), user_list({}) or user_won_list({}) is not list or Member or User".format( type( user_list ), type( user_won_list ) ), error=True, log=True )
            return

        for user_w in user_list:
            for user_l in user_won_list:
                if user_w.id == user_l.id:
                    main.print_date( "{}({}) tried to lose against himself for some reason, removing him from lists...".format(user_w.name, user_w.id ) )
                    user_list.remove( user_w )
                    user_lost_list.remove( user_l )
                    if len( user_list ) == 0:
                        return

        for user_ in user_list:
            self.createDefaults(self, guild, user_ )
            stat_dict[str( guild.id )][str( user_.id )]["losses"] += 1
            stat_dict[str( guild.id )][str( user_.id )]["games"] += 1

            for won_user in user_won_list:
                if won_user.id not in stat_dict[str( guild.id )][str( user_.id )]["unique_losses"]:
                    stat_dict[str( guild.id )][str( user_.id )]["unique_losses"].append( won_user.id )

        if chk_win:
            self.win( guild, user_won_list, user_list, chk_loss=False )

    def get_stat_dict(self):
        global stat_dict
        return stat_dict

    def set_stat_dict(self,bruh):
        global stat_dict
        stat_dict = bruh

    def createDefaults(self, guild, user):
        global stat_dict
        # Guild not in stat_dict
        if str( guild.id ) not in stat_dict:
            temp_dict = dict()
            temp_dict[str( user.id )] = dict()
            stat_dict[str( guild.id )] = temp_dict
        # User not in stat_dict but guild is
        elif str( user.id ) not in stat_dict[str( guild.id )]:
            temp_dict = dict()
            temp_dict[str( user.id )] = dict()
            stat_dict[str( guild.id )].update( temp_dict )
        # "Wins" not under user
        if "wins" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["wins"] = 0
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        # "Unique_wins" not under user
        if "unique_wins" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["unique_wins"] = list()
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        # "Wins" not under user
        if "losses" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["losses"] = 0
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        # "Unique_wins" not under user
        if "unique_losses" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["unique_losses"] = list()
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        if "games" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["games"] = 0
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        if "draws" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["draws"] = 0
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )
        if "surrenders" not in stat_dict[str( guild.id )][str( user.id )]:
            temp_dict = dict()
            temp_dict["surrenders"] = 0
            stat_dict[str( guild.id )][str( user.id )].update( temp_dict )


    def toList(self, user):
        if type( user ) == Member or type( user ) == User:
            return [user]
        elif type( user ) == list:
            return user
        else:
            return None