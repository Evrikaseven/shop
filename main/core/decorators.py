import functools


def roles_allowed(roles=None):
    if not roles:
        roles = []
    def decor(func):
        functools.wraps(func)
        def wrapped(*args, **kwargs):
            pass
        return wrapped
    return decor

