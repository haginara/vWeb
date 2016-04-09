from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from vsm.models import User

from functools import wraps
vshield = settings.VS

"""
http://django.zone/blog/posts/custom-authentication-backends-django/
http://www.djangorocks.com/tutorials/creating-a-custom-authentication-backend/creating-the-imap-authentication-backend.html
"""
class AuthBackend(object):
    def authenticate(self, username=None, password=None):
        if username and password:
            session = vshield.init_session(username, password)
            if vshield.ping(session):
                user, created = User.objects.get_or_create(username=username, session=session)
                if created:
                    user.expired = False
                    user.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.object.get(pk=user_id)
        except User.DoesNotExist:
            return None


def vsm_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """ How to use
    vsm_login_required('app.perm', template='denied.html')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if request.session:
                logger.info("Session: %s" % str(request.session.keys()))

            if 'userid' not in request.session.keys():
                logger.info("userid is not in session")
                response = HttpResponseRedirect(login_url)
                return response
            logger.debug("UserID: %s" % request.session['userid'])
            return f(request, *args, **kwargs)
        return wrapper
    return decorator
