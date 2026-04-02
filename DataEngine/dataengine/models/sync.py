from uuid import uuid4

from django.db import models


class CommonSyncInfo(models.Model):
    class Meta:
        abstract = True
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.TextField(verbose_name="Bonus Level Name")
    vhost = models.ForeignKey('parameters.VHost',null=True,on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True)
    system_object_type = models.TextField(verbose_name="System Object Type",null=True)
    system_object_uuid = models.UUIDField(verbose_name="System Object UUID",null=True)
    driver_package = models.TextField(verbose_name="Driver Package")
    driver_object_type = models.TextField(verbose_name="Driver Object Type")
    driver_object_uuid = models.UUIDField(verbose_name="Driver Object UUID")
    manual_entry = models.BooleanField(default=False)
    def __str__(self):
        return f"Sync Status Object: {self.system_object_type} {self.system_object_uuid} <--> {self.driver_object_type} {self.driver_object_uuid}"


class TeamSyncStatus(CommonSyncInfo):
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE,null=True)


class GroupSyncStatus(CommonSyncInfo):
    group = models.ForeignKey('sports.Group', on_delete=models.CASCADE,null=True)

class SeasonSyncStatus(CommonSyncInfo):
    season = models.ForeignKey('sports.Season', on_delete=models.CASCADE,null=True)

class SportSyncStatus(CommonSyncInfo):
    sport = models.ForeignKey('sports.Sport', on_delete=models.CASCADE,null=True)

class PlayerSyncStatus(CommonSyncInfo):
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE,null=True)

class MatchSyncStatus(CommonSyncInfo):
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE,null=True)

class OddsSyncStatus(CommonSyncInfo):
    matchOdds = models.ForeignKey('odds.MatchOddsSummary', on_delete=models.CASCADE,null=True)

class SegmentSyncStatus(CommonSyncInfo):
    segment = models.ForeignKey('outcomes.Segment', on_delete=models.CASCADE,null=True)

class OutcomeSyncStatus(CommonSyncInfo):
    outcome = models.ForeignKey('outcomes.Outcome', on_delete=models.CASCADE,null=True)


class OutcomeSegmentScoreSyncStatus(CommonSyncInfo):
    segment_score = models.ForeignKey('outcomes.OutcomeSegmentScore', on_delete=models.CASCADE,null=True)


class OutcomeTeamsSyncStatus(CommonSyncInfo):
    team = models.ForeignKey('outcomes.OutcomeTeams', on_delete=models.CASCADE,null=True)
