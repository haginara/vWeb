from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME

from vcd.models import User

from functools import wraps
vcd = settings.VCD
"""
http://django.zone/blog/posts/custom-authentication-backends-django/
http://www.djangorocks.com/tutorials/creating-a-custom-authentication-backend/creating-the-imap-authentication-backend.html
"""


class AuthBackend(object):
    def authenticate(self, username=None, org=None, password=None):
        if username and password and org:
            try:
                token = vcd.init_session(username, org, password)
            except Exception as e:
                logger.error("Exception on authentication: ", str(e))
                return None
            user, created = User.objects.get_or_create(username=username)
            print(user, created)
            if created:
                user.token = token
                user.org = org
                user.expired = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.object.get(pk=user_id)
        except User.DoesNotExist:
            return None


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """ How to use
    login_required('app.perm', template='denied.html')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if request.session:
                print ("Session: %s" % str(request.session.keys()))

            if 'userid' not in request.session.keys():
                print("userid is not in session")
                response = HttpResponseRedirect(login_url)
                print("Response : %s" % response)
                return response
            print ("UserID: %s" % request.session['userid'])
            return f(request, *args, **kwargs)
        return wrapper
    return decorator
