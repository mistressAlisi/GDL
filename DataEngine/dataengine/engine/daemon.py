import importlib

from .abc import ABCDataEngineObj

class DataEngineAPIDaemon(ABCDataEngineObj):
    daemons = {}
    processes = {}
    def _load_driver_daemons(self,driver):
        _driver_daemons = importlib.import_module(f"{driver.class_name}.driver.daemons")
        self.daemons[driver.class_name] = _driver_daemons.DRIVER_API_DAEMONS
        # print(self.daemons)

    def call_driver_method(self,method,**kwargs):
        method = getattr(self.currentDriverObject,method)
        if method:
            return method(**kwargs)



    def start(self):
        for driver in self.drivers:
            self._load_driver_daemons(driver.driver)
        first_process = False
        for driver,classes in self.daemons.items():
            local_classes = []
            for cls in classes:
                print(f"Starting Daemon {cls.__name__}...")
                print(cls)
                daemonObj = cls()
                daemonObj.setup(self.vhost,self.debug)
                print(daemonObj)
                # daemonObj.data_setup_run()
                daemonObj.start()
                local_classes.append(daemonObj)
                if not first_process:
                    first_process = daemonObj
                # daemonObj.join()
            self.processes[driver] = local_classes
        daemonObj.join()
