# import functools
# from django.http import HttpResponseForbidden
# from main.core.constants import Roles


# def disable_for_other_users(func):
#     @functools.wraps(func)
#     def wrapped(*args, **kwargs):
#         return HttpResponseForbidden('12313')
#         # return func(*args, **kwargs)
#     return wrapped
