from odds.models import Match_H2H_H1, Match_H2H_H2, Match_H2H_Q1, Match_H2H_Q2, Match_H2H_Q3, Match_H2H_Q4, Match_First_TD, Match_Anytime_TD, Match_Pass_TD, Match_Pass_YDS, Match_Last_TD, Match_Reception_YDS, Match_Rush_YDS, Match_TD_Over, Match_Spreads_H1, Match_Spreads_H2, Match_Spreads_Q1, Match_Spreads_Q2, Match_Spreads_Q3, Match_Spreads_Q4, Match_Totals_H1, Match_Totals_H2, Match_Totals_Q1, Match_Totals_Q2, Match_Totals_Q3, Match_Totals_Q4, Match_Reception_Longest, Match_Reception, Match_Player_Points, \
    Match_Player_Rebounds, Match_Player_Assists, Match_Player_Threes, Match_Player_Blocks, Match_Player_Steals, Match_Player_Block_Steals, Match_Player_Turnovers, Match_Player_Points_Rebounds_Assists, Match_Player_Rebounds_Assists, Match_Player_First_Basket, Match_Player_Double_Double, Match_Player_Triple_Double, Match_Player_Points_Rebounds, Match_Player_Points_Assists, Match_Player_Points_View, Match_Player_Rebounds_View, Match_Player_Assists_View, Match_Player_Threes_View, Match_Player_Blocks_View, \
    Match_Player_Steals_View, Match_Player_Block_Steals_View, Match_Player_Turnovers_View, Match_Player_Points_Rebounds_Assists_View, Match_Player_Points_Rebounds_View, Match_Player_Points_Assists_View, Match_Player_Rebounds_Assists_View, Match_Player_First_Basket_View, Match_Player_Double_Double_View, Match_Player_Triple_Double_View, Match_Team_Totals_Q4_View, Match_Team_Totals_Q3_View, Match_Team_Totals_Q2_View, Match_Team_Totals_Q1_View
from odds.models import Match_H2H_H1_View, Match_H2H_H2_View, Match_H2H_Q1_View, Match_H2H_Q2_View, Match_H2H_Q3_View, Match_H2H_Q4_View,  Match_First_TD_View, Match_Anytime_TD_View, Match_Pass_TD_View, Match_Pass_YDS_View, Match_Last_TD_View, Match_Reception_YDS_View, Match_Rush_YDS_View, Match_TD_Over_View, Match_Spreads_H1_View, Match_Spreads_H2_View, Match_Spreads_Q1_View, Match_Spreads_Q2_View, Match_Spreads_Q3_View, Match_Spreads_Q4_View, Match_Totals_H1_View, Match_Totals_H2_View, Match_Totals_Q1_View, Match_Totals_Q2_View, Match_Totals_Q3_View, Match_Totals_Q4_View, Match_Reception_Longest_View, Match_Reception_View,Match_Team_Totals_Q1, Match_Team_Totals_Q2, Match_Team_Totals_Q3, Match_Team_Totals_Q4


class OddsMarketMapping:
    market_map = {
        "h2h_h1":Match_H2H_H1,
        "h2h_h2":Match_H2H_H2,
        "h2h_q1":Match_H2H_Q1,
        "h2h_q2":Match_H2H_Q2,
        "h2h_q3":Match_H2H_Q3,
        "h2h_q4":Match_H2H_Q4,
        "player_1st_td":Match_First_TD,
        "player_anytime_td":Match_Anytime_TD,
        "player_pass_tds":Match_Pass_TD,
        "player_pass_yds":Match_Pass_YDS,
        "player_last_td":Match_Last_TD,
        "player_reception_longest":Match_Reception_Longest,
        "player_reception_yds":Match_Reception_YDS,
        "player_receptions": Match_Reception,
        "player_rush_yds":Match_Rush_YDS,
        "player_tds_over":Match_TD_Over,
        "player_points": Match_Player_Points,
        "player_rebounds": Match_Player_Rebounds,
        "player_assists": Match_Player_Assists,
        "player_threes": Match_Player_Threes,
        "player_blocks": Match_Player_Blocks,
        "player_steals": Match_Player_Steals,
        "player_blocks_steals": Match_Player_Block_Steals,
        "player_turnovers": Match_Player_Turnovers,
        "player_points_rebounds_assists": Match_Player_Points_Rebounds_Assists,
        "player_points_rebounds": Match_Player_Points_Rebounds,
        "player_points_assists": Match_Player_Points_Assists,
        "player_rebounds_assists": Match_Player_Rebounds_Assists,
        "player_first_basket": Match_Player_First_Basket,
        "player_double_double": Match_Player_Double_Double,
        "player_triple_double": Match_Player_Triple_Double,
        "spreads_h1":Match_Spreads_H1,
        "spreads_h2":Match_Spreads_H2,
        "spreads_q1":Match_Spreads_Q1,
        "spreads_q2":Match_Spreads_Q2,
        "spreads_q3":Match_Spreads_Q3,
        "spreads_q4":Match_Spreads_Q4,
        "totals_h1":Match_Totals_H1,
        "totals_h2":Match_Totals_H2,
        "totals_q1":Match_Totals_Q1,
        "totals_q2":Match_Totals_Q2,
        "totals_q3":Match_Totals_Q3,
        "totals_q4":Match_Totals_Q4,
        "team_totals_q1": Match_Team_Totals_Q1,
        "team_totals_q2": Match_Team_Totals_Q2,
        "team_totals_q3": Match_Team_Totals_Q3,
        "team_totals_q4": Match_Team_Totals_Q4,
    }

    market_view_map = {
        "h2h_h1":Match_H2H_H1_View,
        "h2h_h2":Match_H2H_H2_View,
        "h2h_q1":Match_H2H_Q1_View,
        "h2h_q2":Match_H2H_Q2_View,
        "h2h_q3":Match_H2H_Q3_View,
        "h2h_q4":Match_H2H_Q4_View,
        "player_1st_td":Match_First_TD_View,
        "player_anytime_td":Match_Anytime_TD_View,
        "player_pass_tds":Match_Pass_TD_View,
        "player_pass_yds":Match_Pass_YDS_View,
        "player_last_td":Match_Last_TD_View,
        "player_reception_longest":Match_Reception_Longest_View,
        "player_reception_yds":Match_Reception_YDS_View,
        "player_receptions": Match_Reception_View,
        "player_rush_yds":Match_Rush_YDS_View,
        "player_tds_over":Match_TD_Over_View,
        "player_points": Match_Player_Points_View,
        "player_rebounds": Match_Player_Rebounds_View,
        "player_assists": Match_Player_Assists_View,
        "player_threes": Match_Player_Threes_View,
        "player_blocks": Match_Player_Blocks_View,
        "player_steals": Match_Player_Steals_View,
        "player_blocks_steals": Match_Player_Block_Steals_View,
        "player_turnovers": Match_Player_Turnovers_View,
        "player_points_rebounds_assists": Match_Player_Points_Rebounds_Assists_View,
        "player_points_rebounds": Match_Player_Points_Rebounds_View,
        "player_points_assists": Match_Player_Points_Assists_View,
        "player_rebounds_assists": Match_Player_Rebounds_Assists_View,
        "player_first_basket": Match_Player_First_Basket_View,
        "player_double_double": Match_Player_Double_Double_View,
        "player_triple_double": Match_Player_Triple_Double_View,
        "spreads_h1":Match_Spreads_H1_View,
        "spreads_h2":Match_Spreads_H2_View,
        "spreads_q1":Match_Spreads_Q1_View,
        "spreads_q2":Match_Spreads_Q2_View,
        "spreads_q3":Match_Spreads_Q3_View,
        "spreads_q4":Match_Spreads_Q4_View,
        "totals_h1":Match_Totals_H1_View,
        "totals_h2":Match_Totals_H2_View,
        "totals_q1":Match_Totals_Q1_View,
        "totals_q2":Match_Totals_Q2_View,
        "totals_q3":Match_Totals_Q3_View,
        "totals_q4":Match_Totals_Q4_View,
        "team_totals_q1": Match_Team_Totals_Q1_View,
        "team_totals_q2": Match_Team_Totals_Q2_View,
        "team_totals_q3": Match_Team_Totals_Q3_View,
        "team_totals_q4": Match_Team_Totals_Q4_View,
    }

    market_datatype_map = {
        "h2h_team":["h2h_q1","h2h_q2","h2h_h1","h2h_q3","h2h_q4","h2h_h2"],
        "spr_team":["spreads_q1","spreads_q2","spreads_h1","spreads_q3","spreads_q4","spreads_h2"],
        "tot_team":["totals_q1","totals_q2","totals_h1","totals_q3","totals_q4","totals_h2",
                    "team_totals_q1","team_totals_q2","team_totals_q3","team_totals_q4"],
        "player": ["player_1st_td", "player_anytime_td", "player_pass_yds", "player_last_td",
                   "player_reception_longest", "player_reception_yds", "player_receptions",
                   "player_rush_yds", "player_tds_over", "player_points", "player_rebounds",
                   "player_assists", "player_threes", "player_blocks", "player_steals",
                   "player_blocks_steals", "player_turnovers", "player_points_rebounds_assists",
                   "player_points_rebounds", "player_points_assists", "player_rebounds_assists",
                   "player_first_basket", "player_double_double","player_triple_double"]


    }

    def get_market_from_type(self,mkt_type):
        if mkt_type in self.market_map:
            return self.market_map[mkt_type]
        else:
            print(f"Warning!! Unable to get Type from {mkt_type}.")
            return False

    def get_market_datatype(self,mkt_type):
        for type in self.market_datatype_map:
            if mkt_type in self.market_datatype_map[type]:
                return type
        return False

    def get_market_view_from_type(self,mkt_type):
        if mkt_type in self.market_map:
            return self.market_view_map[mkt_type]
        else:
            print(f"Warning!! Unable to get Type View from {mkt_type}.")
            return False

    def get_market_views_for_match(self,data_type,matchObj):
        if data_type in self.market_datatype_map:
            return_objs = []
            total_lines = 0
            for dtm in self.market_datatype_map[data_type]:
                data = self.market_view_map[dtm].objects.filter(match=matchObj)
                total_lines += data.count()
                rdata = {"mkt":dtm,"data":data,"name":self.market_map[dtm]._meta.verbose_name}
                return_objs.append(rdata)
            return return_objs,total_lines

    def get_market_dict_views_for_match(self,data_type,matchObj):
        if data_type in self.market_datatype_map:
            return_objs = {}
            total_lines = 0
            for dtm in self.market_datatype_map[data_type]:
                data = self.market_view_map[dtm].objects.filter(match=matchObj)
                if len(data) > 0:
                    total_lines += data.count()
                    rdata = {"mkt":dtm,"data":data[0],"puuid":data[0].pk,"name":self.market_map[dtm]._meta.verbose_name}
                    return_objs[dtm] = rdata
            return return_objs,total_lines

    def get_markets_for_match(self,data_type,matchObj,avg_data=False):
        if data_type in self.market_datatype_map:
            return_objs = []
            total_lines = 0
            for dtm in self.market_datatype_map[data_type]:
                data = self.market_map[dtm].objects.filter(match=matchObj)
                rdata = {"mkt":dtm,"data":data,"name":self.market_map[dtm]._meta.verbose_name}
                olen = len(data)
                if olen > 0:
                    if avg_data:
                        hp = 0
                        ap = 0
                        hP = 0
                        aP = 0
                        if data_type == "h2h_team":
                            for do in data:
                                hp += do.home_price
                                ap += do.away_price
                            rdata["avg"] = {"home_price":hp/olen,"away_price":ap/olen}
                        elif data_type == "spr_team":
                            for do in data:
                                hp += do.home_price
                                hP += do.home_point
                                ap += do.away_price
                                aP += do.away_point
                            rdata["avg"] = {"home_price": hp / olen, "away_price": ap / olen, "home_point": hP/olen, "away_point": aP/olen}
                        elif data_type == "tot_team":
                            for do in data:
                                hp += do.over_price
                                hP += do.over_point
                                ap += do.under_price
                                aP += do.under_point
                            rdata["avg"] = {"over_price": hp/olen,"over_point":hP/olen,"under_price":ap/olen,"under_point":aP/olen}
                            if "team" in data:
                                rdata["avg"]["team"] = data["team"]
                    total_lines += olen
                return_objs.append(rdata)
            if avg_data:
                return return_objs,total_lines
            else:
                return return_objs
        else:
            return False

