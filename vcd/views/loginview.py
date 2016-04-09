from __future__ import absolute_import

# Django
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate

from vcd.forms import LoginForm
from django.conf import settings
vcd = settings.VCD

import logging
logger = logging.getLogger(__name__)


def login_user(request):
    logger.debug("Called login_user in vcd")
    c = dict()
    form = LoginForm()
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.data['username']
            org = form.data['org']
            password = form.data['password']
            logger.debug("Try to login username@org: %s%s" % (username, org))
            user = authenticate(username=username, org=org, password=password)
            if user is not None:
                request.session['userid'] = user.token
                # Set the expiration time to 30mins = 1800s
                request.session.set_expiry(1800)
                logger.debug("added the session : %s" % str(request.session))
                return HttpResponseRedirect("/vcd")
        else:
            logger.error("Invalid Form: %s" % str(form.errors))

    c['form'] = form
    return render_to_response("login_vcd.html", c, context_instance=RequestContext(request))


def logout_user(request):
    user = getattr(request, "user", None)
    logger.debug("User: {}".format(user))
    if hasattr(user, 'is_authenticated') and not user.is_authenticated:
        user = None
    vcd.del_session()
    request.session.flush()

    return HttpResponseRedirect("/vcd/login")
