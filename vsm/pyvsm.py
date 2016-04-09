import requests
import json
import base64
urllib3 = None
try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    urllib3 = None

from functools import wraps

#'https://vsm.nxus.com/api'
class vshield(object):
    def __init__(self, url, username=None, password=None):
        self.api = '{http://www.vmware.com/}'
        self.url = url
        if username and password:
            self.token = self.init_session(username, password)

    def init_session(self, username, password):
        base64string = base64.encodestring(
            "%s:%s" % (username, password))[:-1]
        return base64string
        
    def headers(accept=None, token=None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                headers = {
                    "Authorization": "Basic %s" % token,
                    "Accept": accept,
                    "Content-Type": accept
                }
                args += (headers,)
                return f(*args, **kwargs)
            return wrapper
        return decorator
        
    def get(self, uri, token, headers, params=None):
        headers['Authorization'] = "Basic %s" % token
        #print("URI: %s%s" % (self.url, uri))
        #print("Headers: %s" % str(headers))
        return requests.get("%s%s" % (self.url, uri), headers=headers, verify=False)
    
    @headers("application/xml")
    def ping(self, token, headers=None):
        response = self.get("/2.0/global/heartbeat", token=token, headers=headers)
        #print("Ping response: %d" % response.status_code)
        return response
        if (response.status_code == 200):
            return True
        else:
            print response.text
        
    @headers("application/json")
    def edges(self, token, headers=None):
        r = self.get("/3.0/edges", token=token, headers=headers)
        if r.status_code != 200:
            print(r.text)
        return json.loads(r.text)['edgePage']['data']
    
    @headers("application/json")
    def edge(self, token, edgeid, headers=None):
        r = self.get("/3.0/edges/%s" % edgeid, token=token, headers=headers)
        if r.status_code != 200:
            print(r.text)
        return json.loads(r.text)

    @headers("application/json")
    def nats(self, token, edgeid, headers=None):
        r = self.get("/3.0/edges/%s/nat/config" % edgeid)
        if r.status_code != 200:
            print(r.text)
        
        return json.load(r.text)

        
    @headers("application/json")
    def ipsets(self, token, id, headers=None):
        r = self.get("/2.0/services/ipset/scope/{}".format(id), token=token, headers=headers)
        if r.status_code != 200:
            #print (r.text)
            return {"status": r.text}
        return json.loads(r.text)
    
    @headers("application/json")
    def appsets(self, token, id, headers=None):
        r = self.get("/2.0/services/application/scope/{}".format(id), token=token, headers=headers)
        if r.status_code != 200:
            #print (r.text)
            return {"status": r.text}
        return json.loads(r.text)
    
    def edge_firewalls(self, token, edgeid):
        return self.edge(token, edgeid)['featureConfigs']['features'][1]['firewallRules']['firewallRules']
    
