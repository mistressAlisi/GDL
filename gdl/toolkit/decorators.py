from django.http import HttpResponseRedirect


def account_login(function):
    """
    The Account_login decorator allows you to declare any view as requiring a player to be logged into an account to be able to access it.
    If they are not logged in; then they will be redirected to the index with ?login=true.
    :param function: Function to decorate.
    :return:
    """
    def _function(request,*args, **kwargs):
        if request.session.get('account_id') is None:
            return HttpResponseRedirect('/?login=true')
        return function(request, *args, **kwargs)
    return _function
