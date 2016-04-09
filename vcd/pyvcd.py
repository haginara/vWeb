import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import base64
import logging

import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.DEBUG)


class VCDError(Exception):
    """Generic PE format error exception."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class vcdirector(object):
    def __init__(self, url, restrict=False):
        self.url = url
        self.api = '{http://www.vmware.com/vcloud/v1.5}'
        self.headers = {
            'Accept': 'application/*+xml;version=1.5'
        }

    def get(self, uri, params=None, headers=None):
        logging.debug("%s", str(self.headers))
        response = requests.get(self.url + uri, params=params, headers=self.headers, verify=False)
        return response

    def post(self, uri, params=None, headers=None):
        response = requests.post(self.url + uri, data=self.headers, verify=False)
        return response

    def init_session(self, username, org, password):
        login = "{username}@{org}:{password}".format(username=username, org=org, password=password)
        base64login = base64.encodestring(login)
        self.headers['Authorization'] = "Basic %s" % base64login
        response = self.post("/sessions", headers=self.headers)
        if response.status_code != 200:
            raise VCDError("Failed to login")

        token = response.headers['x-vcloud-authorization']
        self.headers['x-vcloud-authorization'] = token
        del self.headers['Authorization']

        #return {'x-vcloud-authorization': token}
        return token

    def del_session(self):
        requests.delete(self.uri + "/session")

    def is_login(self):
        return True if 'x-vcloud-authtorization' in self.headers else False

    def orgs(self, org_name=None):
        response = self.get("/org", headers=self.headers)
        if response.status_code != 200:
            raise VCDError("Failed to retrive org list")
        
        data = ET.fromstring(response.text)
        list_orgs = [{"org": element.items()[2][1], "url": element.items()[0][1]} for element in data.getchildren()]
        if org_name:
            for org in list_orgs:
                if org_name.lower() == org['org'].lower():
                    return org
        return list_orgs

    def virtualmachines(self, org_name=None, vm_name=None):
        page = 1
        params = {
            "type": "vm",
            "pageSize": 100,
            "page": page
        }
        vmrecords = list()
        """
        ['status', 'hardwareVersion', 'vmToolsVersion', 'memoryMB', 'href', 'guestOs', 'isDeployed', 'isInMaintenanceMode', 'isVAppTemplate', 'networkName', 'isDeleted', 'containerName', 'task', 'container','name', 'isVdcEnabled', 'pvdcHighestSupportedHardwareVersion', 'isPublished', 'taskStatus', 'numberOfCpus', 'vdc', 'isBusy', 'taskDetails', 'taskStatusName']
        """
        while True:
            response = self.get('/query', params=params)
            data = ET.fromstring(response.text)
            total = int(data.attrib['total'])
            vmrecords += [element.attrib for element in filter(lambda e: 'VMRecord' in e.tag, data)]
            logging.debug("# of vmrecords: %d", len(vmrecords))
            if total <= len(vmrecords):
                break
            page += 1
        logging.debug("Total of vmrecords: %d/%d", len(vmrecords), total)
        if vm_name:
            vmrecords = filter(lambda vm: vm_name.lower() in vm['name'].lower(), vmrecords)
        return vmrecords

    def network(self, href):
        response = self.get("/vApp/%s/networkConnectionSection" % href.split("/")[-1])
        if response.status_code != 200:
            raise VCDError("Failed to retrive the netwok information")
        data = ET.fromstring(response.text)
        netinfos = list()
        for element in data.findall(self.api + "NetworkConnection"):
            netinfo = {'network': element.attrib['network']}
            for info in element:
                tag = info.tag.replace(self.api, "")
                netinfo[tag] = info.text
            netinfos.append(netinfo)
        return netinfo
