from asgiref.sync import sync_to_async

from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT, GRADER_MATCH_FINISHED_STATUS_LONG
from outcomes.models import Outcome, OutcomeTeams,OutcomeSegmentScore


class OutcomesEngine(object):
    def __init__(self, vhost,**kwargs):
        self.vhost = vhost
        self.useable_segments = [f"inning_{i}" for i in range(1, 10)]+[f"quarter_{i}" for i in range(1, 5)]+[f"Set {i}" for i in range(1, 10)]+["fulltime","halftime","extratime","penalty"]
    def get_outcomes(self,match):
        outcomes = []
        tennis_score = match.sport.group.slug == "TN"
        outcomeObjs = Outcome.objects.filter(vhost=self.vhost,match=match)
        for outcomeObj in outcomeObjs:
            _segObjs = OutcomeSegmentScore.objects.filter(outcome=outcomeObj,vhost=self.vhost)
            _teamObjs = OutcomeTeams.objects.filter(outcome=outcomeObj,vhost=self.vhost)
            htObj = _teamObjs.filter(team__name__icontains=outcomeObj.match.home_team.name).first()
            atObj = _teamObjs.filter(team__name__icontains=outcomeObj.match.away_team.name).first()
            out_data = {
                "outcome":outcomeObj,
                "segments":{
                    "home":{

                    },
                    "away":{

                    }
                },
                "teams":{
                    "home":htObj,
                    "away":atObj,
                }
            }
            home_total = 0
            away_total = 0
            if tennis_score:
                # print("TENNIS SCORE!!")
                score_struct = {

                }
                for z in _segObjs.order_by("-segment"):
                    if z.segment not in score_struct:
                        score_struct[z.segment] = {
                        "home":0,
                        "away":0,
                        }
                    if z.team == match.home_team and z.segment in self.useable_segments:
                        out_data["segments"]["home"][z.segment] = z.score
                        score_struct[z.segment]["home"] = z.score
                    elif z.team == match.away_team and z.segment in self.useable_segments:
                        out_data["segments"]["away"][z.segment] = z.score
                        score_struct[z.segment]["away"] = z.score
                for k,v in score_struct.items():
                    if v["home"] > v["away"]:
                        home_total += 1
                    elif v["home"] < v["away"]:
                        away_total += 1

            else:

                for seg in _segObjs.filter(team__name__icontains=outcomeObj.match.home_team.name):
                    # print(seg)
                    out_data["segments"]["home"][seg.segment] = seg.score
                    if seg.segment in self.useable_segments:
                        home_total += seg.score



                for seg in _segObjs.filter(team__name__icontains=outcomeObj.match.away_team.name):
                    out_data["segments"]["away"][seg.segment] = seg.score
                    if seg.segment in self.useable_segments:
                        away_total += seg.score
            out_data["totals"] = {"home":home_total, "away":away_total}
            outcomes.append(out_data)
        # print(len(outcomes))
        # print(outcomes[0]["totals"])
        return outcomes


    def get_final_scores(self,match):
        # print("aA")
        outcomes = self.get_all_scores(match)
        final_outcomes = {}
        # print("aB")
        for key,vals in outcomes.items():

            if key not in final_outcomes:
                final_outcomes[key] = False
            for val in vals:
                # print(vals)
                if "status" in val:
                    if "is_end_game" in val["status"] or "is_end_segment" in val["status"]:
                        if val["status"]["is_end_game"] == True:
                            final_outcomes[key] = val

                        elif val["status"]["is_end_segment"] == True:
                            final_outcomes[key] = val
                    elif "status_short" in val["status"] or "status_long" in val["status"]:
                        if val["status"]["status_short"] in GRADER_MATCH_FINISHED_STATUS_SHORT:
                            final_outcomes[key] = val
                        elif val["status"]["status_long"] in GRADER_MATCH_FINISHED_STATUS_LONG:
                            final_outcomes[key] = val
        return final_outcomes

    def get_all_scores(self,match):
        tennis_score = match.sport.group.slug == "TN"
        outcomes = {
        }
        _outObj = self.get_outcomes(match)
        # print(f"M' {match.uuid}")
        # print(len(_outObj))
        hs_a = []
        as_a = []
        for outObj in _outObj:
            # print(outObj["totals"])
            # print(outObj["teams"])
            hs_a = []
            as_a = []
            home_score = 0
            away_score = 0
            if not tennis_score:
                oshk = outObj["segments"]["home"].keys()
                if len(oshk) > 0:
                    for o in oshk:
                        if o in self.useable_segments:
                            # print(outObj["segments"]["home"][o])
                            home_score += outObj["segments"]["home"][o]
                ashk = outObj["segments"]["away"].keys()
                # print("aaaa")
                if len(ashk) > 0:
                    for a in ashk:
                        if a in self.useable_segments:
                            # print(outObj["segments"]["away"][a])
                            away_score += outObj["segments"]["away"][a]
                hs_a.append(home_score or 0)
                # print(outObj["teams"]["home"])
                if outObj["teams"]["home"]:
                    # print(f"Home Team: {outObj["teams"]["home"].score}")
                    hs_a.append(outObj["teams"]["home"].score or 0)
                    hsf = outObj["teams"]["home"].score or 0
                else:
                    hsf = 0
                # print(away_score)
                as_a.append(away_score or 0)
                # print(hs_a)
                # print(as_a)
                if outObj["teams"]["away"]:
                    # print(f"Away Team: {outObj["teams"]["away"].score}")
                    as_a.append(outObj["teams"]["away"].score or 0)
                    asf = outObj["teams"]["away"].score or 0
                else:
                    asf = 0
                # print('Totl:')
                # print(outObj["totals"])

            if "home" in outObj["totals"]:
                hs_a.append(outObj["totals"]["home"] or 0)
                if tennis_score:
                    hsf = outObj["totals"]["home"] or 0
            if "away" in outObj["totals"]:
                as_a.append(outObj["totals"]["away"] or 0)
                if tennis_score:
                    asf = outObj["totals"]["away"] or 0
            # print(hs_a)
            # print(as_a)
            result_outcomes = {
                               "status":{
                                   "clock":outObj["outcome"].clock,
                                   "status_short":outObj["outcome"].status_short,
                                   "status_long":outObj["outcome"].status_long,
                                   "is_current":outObj["outcome"].is_current,
                                   "is_start_game":outObj["outcome"].is_start_game,
                                   "is_end_game":outObj["outcome"].is_end_game,
                                   "is_start_segment":outObj["outcome"].is_start_segment,
                                   "is_end_segment":outObj["outcome"].is_end_segment

                               },
                               "home": hsf,
                               "away": asf,
                               "segments":outObj["segments"],
                               "totals":outObj["totals"],
                               "computed_score": {
                                   "home": home_score,
                                   "away": away_score,
                               },
                               "score":{
                                   "home": max(hs_a),
                                   "away": max(as_a),
                               }
                               }
            if outObj["outcome"].driver not in outcomes:
                outcomes[outObj["outcome"].driver] = []
            outcomes[outObj["outcome"].driver].append(result_outcomes)
        # print(hs_a)
        # print(as_a)
        return outcomes

    def get_final_score_frontend(self,match):
        """
        Get the final scores of a match object specifically for frontend rendering.
        This function will find the best score across all driver results.
        :param match:
        :return: home_score, away_score (just Numbers)
        """
        home_scores = []
        away_scores = []
        tennis_score = match.sport.group.slug == "TN"
        outcomes = self.get_final_scores(match)
        if tennis_score:
            home_score = 0
            away_score = 0
            for key,item in outcomes.items():
                if item != False:
                        if item["score"]["home"] > item["score"]["away"]:
                            home_score += 1
                        elif item["score"]["home"] < item["score"]["away"]:
                            away_score += 1
            return home_score, away_score
        else:
            for key,item in outcomes.items():
                if item:
                    home_scores.append(item["score"]["home"] or 0)
                    away_scores.append(item["score"]["away"] or 0)
                    print(item["status"]["status_short"])
            # print(home_scores)
            # print(away_scores)

            if len(home_scores) > 0:
                home_score = max(home_scores)
            else:
                home_score = 0
            if len(away_scores) > 0:
                away_score = max(away_scores)
            else:
                away_score = 0
            return home_score, away_score


    def get_score_frontend(self,match):
        """
        Get the live scores of a match object specifically for frontend rendering.
        This function will find the best score across all driver results.
        :param match:
        :return: home_score, away_score (just Numbers)
        """
        home_scores = []
        away_scores = []
        tennis_score = match.sport.group.slug == "TN"
        outcomes = self.get_all_scores(match)
        # Select outcome based on driver:
        odata = False
        if "apisports.match.*" in outcomes:
            odata = outcomes["apisports.match.*"][0]
        elif "apitennis.fixture.Fixture" in outcomes:
            odata = outcomes["apitennis.fixture.Fixture"][0]
        elif "dataengine.drivers.kiblio" in outcomes:
            odata = outcomes["dataengine.drivers.kiblio"][::1][0]
        if odata:
            home_score = odata["score"]["home"]
            away_score = odata["score"]["away"]
            status = odata["status"]["status_long"]
            return home_score, away_score, status
        else:
            return False, False, False


    def get_final_score_summary(self,match):
        hsa = []
        asa = []
        for n,data in self.get_final_scores(match).items():
            if data:
                if "score" in data:
                    if "home" in data["score"]:
                        hsa.append(data["score"]["home"])
                    if "away" in data["score"]:
                        asa.append(data["score"]["away"])
        if len(hsa) > 0:
            hst = max(hsa)
        else:
            hst = 0
        if len(asa) > 0:
            ast = max(asa)
        else:
            ast = 0
        return {"home":hst,"away":ast}


