def user_groups(request):
    if not request.user.is_authenticated:
        return {"user_groups": []}

    groups = list(request.user.groups.values_list("name", flat=True))
    return {"user_groups": groups}