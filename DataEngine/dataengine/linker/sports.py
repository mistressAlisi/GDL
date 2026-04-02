import importlib

from django.db.models import Q

from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import SportSyncStatus, GroupSyncStatus
from sports.models import Sport, Group


class DataEngineLinker(DataEngineAPIDaemon):
    def start(self):
        for driver in self.drivers:
            # print(driver)
            self._load_driver(driver.driver)
            data = self.call_driver_method("get_sports_groups")
            self.logger.info(f"Loaded {len(data)} groups from {driver.driver}")
            # print(data)
            self.sync_groups_data(data)
            data = self.call_driver_method("get_sports_sports")
            self.logger.info(f"Loaded {len(data)} sports from {driver.driver}")
            # print(data)
            self.sync_sports_data(data)


    def sync_groups_data(self,data):
        for input in data:
            self.logger.info(f'Linking input sport group: {input["name"]} from {input["object_type"]}[{input["object_uuid"]}]')
            # Look for the data sync:
            try:
                dataSync = GroupSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=input["object_type"],
                    driver_object_uuid=input["object_uuid"],
                )
                self.logger.info(f'Group already linked as {dataSync.group.uuid}.')
            except GroupSyncStatus.DoesNotExist:
                # Sync Map does not exist - Let's create it:
                self.logger.info(f'Group is not linked; seeking candidates....')
                candidates = Group.objects.filter((Q(slug__icontains=input["slug"])|Q(name__icontains=input["name"]))&Q(vhost=self.vhost))
                if len(candidates) < 1:
                    # Must create here.
                    self.logger.info(f'No sport groups found for {input["name"]}: Creating it!')
                    sportGroup = Group.objects.create(name=input["name"], slug=input["slug"],vhost=self.vhost)
                    sportGroup.save()
                elif len(candidates) == 1:
                    # Single candidate; just link:
                    sportGroup = candidates[0]

                gssObj = GroupSyncStatus.objects.get_or_create(
                    vhost=self.vhost,
                    driver_object_type=input["object_type"],
                    driver_object_uuid=input["object_uuid"],
                )[0]
                gssObj.group = sportGroup
                gssObj.save()
                self.logger.info(f"Found {sportGroup.name} sport group for {input['name']}: Linked!")

    def sync_sports_data(self, data):
        for dRow in data:
            self.logger.info(f'Linking input sport: {dRow["title"]} from {dRow["object_type"]}[{dRow["object_uuid"]}]')
            # Look for the data sync:
            try:
                dataSync = SportSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=dRow["object_type"],
                    driver_object_uuid=dRow["object_uuid"],
                )
                self.logger.info(f'Sport already linked as {dataSync.sport.uuid}.')
            except SportSyncStatus.DoesNotExist:
                # Sync Map does not exist - Let's create it:
                self.logger.info(f'Group is not linked; seeking candidates....')
                candidates = Sport.objects.filter((Q(key__icontains=dRow["key"])|Q(title__icontains=dRow["title"]))&Q(vhost=self.vhost))
                lca = len(candidates)
                if lca < 1:
                    # Must create here.
                    self.logger.info(f'No sport groups found for {dRow["title"]}: Creating it!')
                    groupObj,cc = Group.objects.get_or_create(vhost=self.vhost,slug=dRow["group_type"])
                    if cc: groupObj.save()
                    sportObj = Sport.objects.create(title=dRow["title"], key=dRow["key"],vhost=self.vhost,group=groupObj)
                    sportObj.save()
                elif lca == 1:
                    # Single candidate; just link:
                    sportObj = candidates[0]
                elif lca > 1:
                    print(f"Multiple Objects found for {dRow["key"]}/{dRow["title"]}:")
                    for c in candidates:
                        print(f"Sport [{c.key}]:'{c.title}'")
                    idata = False
                    while not idata:
                        idata = input("Input selection (key), or 'c' to create a new sport >> ")
                        if idata == 'c':
                            groupObj, cc = Group.objects.get_or_create(vhost=self.vhost, slug=dRow["group_type"],name=dRow["group_type"])
                            if cc: groupObj.save()
                            sportObj = Sport.objects.create(title=dRow["title"], key=dRow["key"], vhost=self.vhost,group=groupObj)
                            sportObj.save()
                            self.logger.info(f"Sport {c.key} created!")
                        else:
                            try:
                                sportObj = candidates.get(key=idata)
                            except Sport.DoesNotExist:
                                idata = False
                                print(f"Sport [{idata}] not found!")
                gssObj = SportSyncStatus.objects.get_or_create(
                    vhost=self.vhost,
                    driver_object_type=dRow["object_type"],
                    driver_object_uuid=dRow["object_uuid"],
                )[0]
                gssObj.sport = sportObj
                gssObj.save()
                self.logger.info(f"Found {sportObj.title} sport for {dRow['title']}: Linked!")



