import importlib

from django.db.models import Q

from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import TeamSyncStatus
from sports.models import Sport, Group
from teams.models import Team


class DataEngineLinker(DataEngineAPIDaemon):
    def start(self):
        for driver in self.drivers:
            # print(driver)
            self._load_driver(driver.driver)
            data = self.call_driver_method("get_teams")
            self.logger.info(f"Loaded {len(data)} teams from {driver.driver}")
            self.sync_teams_data(data)
            # print(data)

    def sync_teams_data(self, data):
        for dRow in data:
            try:
                self.logger.info(f'Linking input team: {dRow["key"]} from {dRow["object_type"]}[{dRow["object_uuid"]}]')
            except Exception as e:
                print(dRow)
                return False
            # Look for the data sync:
            try:
                dataSync = TeamSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=dRow["object_type"],
                    driver_object_uuid=dRow["object_uuid"],
                )
                self.logger.info(f'Team already linked as {dataSync.team.uuid}.')
            except TeamSyncStatus.DoesNotExist:
                # Sync Map does not exist - Let's create it:
                self.logger.info(f'Team is not linked; seeking candidates....')
                candidates = Team.objects.filter((Q(key__icontains=dRow["key"])|Q(name__icontains=dRow["name"]))&Q(vhost=self.vhost))
                lca = len(candidates)
                if lca < 1:
                    # Must create here.
                    self.logger.info(f'No Teams found for {dRow["name"]}: Creating it!')
                    teamObj,cc = Team.objects.get_or_create(vhost=self.vhost,key=dRow["key"],name=dRow["name"])
                    if cc: teamObj.save()
                elif lca == 1:
                    # Single candidate; just link:
                    teamObj = candidates[0]
                elif lca > 1:
                    print(f"Multiple Objects found for {dRow["key"]}/{dRow["name"]}:")
                    for c in candidates:
                        print(f"Sport [{c.key}]:'{c.name}'")
                    idata = False
                    while not idata:
                        idata = input("Input selection (key), or 'c' to create a new sport >> ")
                        if idata == 'c':
                            teamObj = Team.objects.create(name=dRow["name"], key=dRow["key"], vhost=self.vhost)
                            teamObj.save()
                            self.logger.info(f"Team {c.key} created!")
                        else:
                            try:
                                teamObj = candidates.get(key=idata)
                            except Sport.DoesNotExist:
                                idata = False
                                print(f"Team [{idata}] not found!")
                gssObj = TeamSyncStatus.objects.get_or_create(
                    vhost=self.vhost,
                    driver_object_type=dRow["object_type"],
                    driver_object_uuid=dRow["object_uuid"],
                )[0]
                gssObj.team = teamObj
                gssObj.save()
                self.logger.info(f"Found {teamObj.name} team for {dRow['name']}: Linked!")