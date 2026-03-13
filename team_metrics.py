def form_points(form):

    if not form:
        return 0

    return form.count("W") * 3 + form.count("D")


def goal_diff(gf, ga):

    return (gf or 0) - (ga or 0)


def volatility(form):

    if not form:
        return 0

    swings = 0

    for i in range(1, len(form)):
        if form[i] != form[i - 1]:
            swings += 1

    return swings