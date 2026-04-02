from management.models import Manager


def get_all_sub_managers(manager):
    """
    Returns a list of all Manager objects nested under the given manager.
    """
    sub_managers = []
    if not manager:
        return sub_managers
    # Find direct reports (where parent is this manager's user)
    direct_reports = Manager.objects.filter(parent=manager.user)

    for sub in direct_reports:
        sub_managers.append(sub)
        # Recurse into each direct report
        sub_managers.extend(get_all_sub_managers(sub))

    return sub_managers