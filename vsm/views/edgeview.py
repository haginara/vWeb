from __future__ import absolute_import

# Django
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings

from vsm.forms import SearchForm

from vsm.auth import vsm_login_required

from functools import wraps
from . import users

import logging
logger = logging.getLogger(__name__)


def server_cache(key, default):
    """ How to use
    server_cache('edges')
    """
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            global users
            print users
            if request.session['userid'] not in users:
                users[request.session['userid']] = dict()
                users[request.session['userid']][key] = default
            return f(request, *args, **kwargs)
        return wrapper
    return decorator


def get_object(ipsets, firewall, target):
    if firewall[target] is None or firewall[target]['groupingObjectId'] is []:
        return ["*"]

    sources = firewall[target]['groupingObjectId']
    objects = list()
    for src in sources:
        try:
            objects.append(filter(lambda ipset: ipset['objectId'] == src, ipsets)[0])
        except IndexError as e:
            print(e)
        "ipset['name'],ipset['obejctid'],ipset['value']"
    return objects
    #return firewall[target]['groupingObjectId']


def get_app_objects(appsets, firewall, target):
    if firewall[target] is None:
        return ["*"]

    apps = firewall['application']['applicationId']
    objects = list()
    for app in apps:
        try:
            objects.append(filter(lambda appset: appset['objectId'] == app, appsets)[0])
        except IndexError as e:
            print(e)
        "ipset['name'],ipset['obejctid'],ipset['value']"
    return objects


@vsm_login_required(login_url="/vsm/login")
@server_cache("edges", None)
def edgeview(request):
    global users
    edges = users[request.session['userid']]['edges']
    if edges is None:
        edges = settings.VS.edges(request.session['userid'])
        users[request.session['userid']]['edges'] = edges

    template = loader.get_template("edges.html")
    form = SearchForm()
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.data['search'].lower()
            print("Searching the : %s" % (search))
            edges = filter(lambda edge: search in edge['name'].lower(), edges)
            context = {'edges': edges, 'form': form}
            return HttpResponse(template.render(context, request))
        else:
            print("Invalid Form: %s" % str(form.errors))
    print "EdgeView: %s" % str(request.session)
    context = {'edges': edges, 'form': form}
    return HttpResponse(template.render(context, request))


@vsm_login_required(login_url="/vsm/login")
@server_cache("edge", {})
def detailview(request, edgeId):
    """/vsm/edge-50
    """
    global users
    print("DetailView")
    template = loader.get_template("edge.html")
    form = SearchForm()
    search = None
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.data['search']
            print("Searching the : %s" % (search))

    nats = settings.VS.nats(request.session['userid'], edgeId)
    edge = settings.VS.edge(request.session['userid'], edgeId)
    ipsets = settings.VS.ipsets(request.session['userid'], edgeId)
    appsets = settings.VS.appsets(request.session['userid'], edgeId)

    firewalls = settings.VS.edge_firewalls(request.session['userid'], edgeId)
    fws = list()
    for firewall in firewalls:
        fw = dict()
        fw['name'] = firewall['name']
        fw['action'] = firewall['action']
        fw['description'] = firewall['description']
        #print [ipset['objectId'] for ipset in ipsets]
        #print fw['name']
        fw['source'] = get_object(ipsets, firewall, 'source')
        fw['destination'] = get_object(ipsets, firewall, 'destination')
        fw['application'] = get_app_objects(appsets, firewall, 'application')
        if search:
            search = search.lower()
            added = False
            search_ipset = fw['source'] + fw['destination']
            try:
                for ipset in search_ipset:
                    if search in ipset['name'].lower() or search in ipset['value'].lower():
                        added = True
                        fws.append(fw)
                if added is False:
                    for appset in fw['application']:
                        if search in appset['name'].lower() or search in str(appset['element']['value']).lower():
                            added = True
                            fws.append(fw)
                if added is False:
                    for value in fw.values():
                        if search in value.lower():
                            added = True
                            fws.append(fw)
            except Exception as e:
                print(e)
        else:
            fws.append(fw)

    context = RequestContext(request, {
        'form': form,
        'edge': edge,
        'ipsets': ipsets,
        'firewalls': fws,
        'nats': nats,
    })
    return HttpResponse(template.render(context))
