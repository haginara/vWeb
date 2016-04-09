from __future__ import absolute_import

# Django
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate

from vsm.forms import LoginForm
#from vsm.auth import authenticate, login, logout
from . import users

import logging
logger = logging.getLogger(__name__)


#@csrf_protect
def login_vsm_user(request):
    # template = loader.get_template("login.html")
    global users
    c = dict()
    #c.update(csrf(request))
    form = LoginForm()
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.data['username']
            password = form.data['password']
            print("Try to login username: %s" % (username))
            user = authenticate(username=username, password=password)
            if user is not None:
                request.session['userid'] = user.session
                # Set the expiration time to 30mins = 1800s
                request.session.set_expiry(1800)
                print("added the session : %s" % str(request.session))
                users[user.session] = {"edges": None}
                return HttpResponseRedirect("/vsm")
        else:
            print("Invalid Form: %s" % str(form.errors))

    c['form'] = form
    return render_to_response("login.html", c, context_instance=RequestContext(request))


def logout_vsm_user(request):
    global users
    user = getattr(request, "user", None)
    print("User: {}".format(user))
    if hasattr(user, 'is_authenticated') and not user.is_authenticated:
        user = None
    request.session.flush()
    return HttpResponseRedirect("/vsm/login")
