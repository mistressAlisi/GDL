import uuid
from django.db import transaction

from django.db import transaction
from django.utils.timezone import now

# from linemanager.hierarchy import Hierarchy

from wager.models import Wager, MatchWagers

def create_application_wager(account,application,vhost,**kwargs):
    """
    Create an Athena Wager based on an Application installed on the platform. The only required parameters are Account, Application, and Vhost.
    All other parameters that are passed on to the kwargs will be passed to the underlying Wager obj if the column exists for the kwargs argument.
    By default, this action creates a metrics event for your application. If you would like to add more information,
    pass the 'application_session', 'url', 'current_ip', and 'account_session' parameters to record on the metrics, or 'no_metrics' to skip
    metrics entirely.
    Application_session and account_session should be metrics session objects for the respective type. URL and Current IP are pretty self explainatory.
    All other parameters of normal wagers are to be passed in the kwargs.
    This action also triggers the wager_created signal, sent with the parameters above, AND the wager uuid.
    :param account: Account Object to create wager for.
    :param application: AvailableApplication Object to create wager for.
    :param vhost:  VHost Object to create wager for.
    :param kwargs: Optional parameters, some are listed above. These one catches all the possible columns of Wager and, it also sets
    current_ip, url, application_session and account_session in the metrics object (if no_metrics is not passed as a boolean to disable.)
    :return: WagerObj.
    """
    wagerObj = Wager(
        account=account,
        application_type=application,
        vhost=vhost,
    )
    # print(kwargs)
    for k,v in kwargs.items():
        if hasattr(wagerObj, k):
            setattr(wagerObj, k, v)

    wagerObj.save()
    if not 'no_metrics' in kwargs:
        metrics_obj = AccountApplicationActivity(account=account,application=application,
                                                 vhost=vhost,action_type="WAGER",
                                                 risk=wagerObj.risk,win=wagerObj.win,
                                                 related_wager=wagerObj)
        for k in ["current_ip","url","application_session","account_session"]:
            if k in kwargs:
                setattr(metrics_obj, k, kwargs[k])
        metrics_obj.save()
        afa,_ = AccountFavouriteApplications.objects.get_or_create(application=application,vhost=vhost,account=account)
        afa.total_actions += 1
        afa.total_wagers += 1
        afa.save()
    from wager.signals import signal_wager_created
    signal_wager_created.send(sender="create_application_wager",wager=wagerObj, account=account,application=application,vhost=vhost)
    return wagerObj