from __future__ import absolute_import

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings

from vcd.forms import SearchForm

from vcd.auth import login_required

import logging
logger = logging.getLogger(__name__)


@login_required(login_url="/vcd/login")
def orgsview(request):
    orgs = settings.VCD.orgs()
    template = loader.get_template("orgs.html")
    form = SearchForm()
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.data['search'].lower()
            logger.debug("Searching the : %s" % (search))
            orgs = filter(lambda edge: search in edge['org'].lower(), orgs)
            context = {'orgs': orgs, 'form': form}
            return HttpResponse(template.render(context, request))
        else:
            logger.error("Invalid Form: %s" % str(form.errors))
    logger.debug("OrgsView: %s" % str(request.session))
    context = {'orgs': orgs, 'form': form}
    return HttpResponse(template.render(context, request))


@login_required(login_url="/vcd/login")
def orgview(request, org):
    virtualmachines = settings.VCD.virtualmachines(org_name=org)
    template = loader.get_template("virtualmachines.html")
    form = SearchForm()
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.data['search'].lower()
            logger.debug("Searching the : %s" % (search))
            virtualmachines = filter(lambda vm: search in vm['name'].lower(), virtualmachines)
            for vm in virtualmachines:
                vm['netinfo'] = settings.VCD.network(vm.href)
            logger.debug("Number of result: ", len(virtualmachines))
            context = {'vms': virtualmachines, 'form': form}
            return HttpResponse(template.render(context, request))
        else:
            logger.error("Invalid Form: %s" % str(form.errors))
    logger.debug("OrgsView: %s" % str(request.session))
    context = {'vms': virtualmachines, 'form': form}
    return HttpResponse(template.render(context, request))
