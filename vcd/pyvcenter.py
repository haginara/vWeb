import atexit

from pyVim import connect
from pyVmomi import vmodl, vim
import requests
requests.packages.urllib3.disable_warnings()
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

import json
import logging
from collections import namedtuple
logger = logging.getLogger(__name__)


def get_view(content, vimtype):
    if not isinstance(vimtype, list):
        raise TypeError

    objView = content.viewManager.CreateContainerView(
        content.rootFolder,
        vimtype, True)
    view = objView.view
    objView.Destroy()
    logger.info("Get View of %s", str(vimtype))
    return view


def len_vms(credential, org):
    try:
        service_instance = connect.SmartConnect(host=credential.host,
                                                user=credential.user,
                                                pwd=credential.password,
                                                port=443)
        content = service_instance.RetrieveContent()
        vm_list = get_view(content, [vim.VirtualMachine])
        logger.debug("# of VM: %d", len(vm_list))
        return len(vm_list)
    except vmodl.MethodFault as error:
        logger.error("Caught vmodl fault : " + error.msg)
    connect.Disconnect(service_instance)
    return 0


def get_device(vm, device):
    devices = filter(isinstance(dev, device) for dev in vm.config.hardware.device)
    return devices


def get_content(credential):
    content = None
    try:
        service_instance = connect.SmartConnect(host=credential.host,
                                                user=credential.user,
                                                pwd=credential.password,
                                                port=443)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
    except vmodl.MethodFault as error:
        logger.error("Caught vmodl fault : %s", error.msg)
        return None
    return content


def nic_info(networks, org):
    dic_nic = {}
    for nic in networks:
        if nic.network:
            network = nic.network.replace(" ", "")
        else:
            network = org
        if nic.ipAddress:
            dic_nic[network] = [ip for ip in nic.ipAddress]
        else:
            dic_nic[network] = None
    return dic_nic


def get_vm_from_view(view, org):
    for vm in view:
        # vm.guest(vim.vim.GuestInfo)
        logger.debug("instanceUuid\t\t: %s" % vm.summary.config.instanceUuid)
        logger.debug("Name\t: %s" % vm.summary.config.name)
        logger.debug("Path\t\t: %s" % vm.summary.config.vmPathName)
        logger.debug("OS\t\t: %s" % vm.summary.config.guestFullName)
        logger.debug("Cpu\t\t: %s" % vm.summary.config.numCpu)
        logger.debug("Memory\t\t: %s" % vm.summary.config.memorySizeMB)
        logger.debug("State\t\t: %s" % vm.summary.runtime.powerState)
        logger.debug("Uptime\t\t: %s" % vm.summary.quickStats.uptimeSeconds)
        logger.debug("Template\t: %s" % vm.summary.config.template)
        logger.debug("Network\t\t: %s" % str(nic_info(vm.guest.net, org)))

        server_name = vm.summary.config.name.split()
        Server = {
            "server_id": vm.summary.config.instanceUuid,
            #"server_name": " ".join(server_name[:-1]) if 1 < len(server_name) else server_name[0],
            "server_name": vm.summary.config.name,
            "vcorg": org,
            'os': vm.summary.config.guestFullName,
            'networks': nic_info(vm.guest.net, org),
            'power': vm.summary.runtime.powerState,
            'cpu': vm.summary.config.numCpu,
            'memory': vm.summary.config.memorySizeMB,
            #'uptimeSecond': 0,
            'template': vm.summary.config.template,
        }
        yield Server


def get_vms(credential, org):
    try:
        service_instance = connect.SmartConnect(host=credential.host,
                                                user=credential.user,
                                                pwd=credential.password,
                                                port=443)

        #atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        vm_list = get_view(content, [vim.VirtualMachine])

        logger.debug("# of VM: %d", len(vm_list))
        for vm in vm_list:
            # vm.guest(vim.vim.GuestInfo)
            logger.debug("instanceUuid\t\t: %s" % vm.summary.config.instanceUuid)
            logger.debug("Name\t: %s" % vm.summary.config.name)
            logger.debug("Path\t\t: %s" % vm.summary.config.vmPathName)
            logger.debug("OS\t\t: %s" % vm.summary.config.guestFullName)
            logger.debug("Cpu\t\t: %s" % vm.summary.config.numCpu)
            logger.debug("Memory\t\t: %s" % vm.summary.config.memorySizeMB)
            logger.debug("State\t\t: %s" % vm.summary.runtime.powerState)
            logger.debug("Uptime\t\t: %s"% vm.summary.quickStats.uptimeSeconds)
            logger.debug("Template\t: %s"% vm.summary.config.template)
            logger.debug("Network\t\t: %s"% str(nic_info(vm.guest.net, org)))

            Server = {
                "server_id": vm.summary.config.instanceUuid,
                "server_name": vm.summary.config.name,
                "vcorg": org,
                'os': vm.summary.config.guestFullName,
                'networks': nic_info(vm.guest.net, org),
                'power': vm.summary.runtime.powerState,
                'cpu': vm.summary.config.numCpu,
                'memory': vm.summary.config.memorySizeMB,
                #'uptimeSecond': vm.summary.quickStats.uptimeSeconds,
                #'uptimeSecond': 0,
                'template': vm.summary.config.template,
            }
            yield Server

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        connect.Disconnect(service_instance)

    connect.Disconnect(service_instance)

def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """
    credentials = json.loads(accounts, object_hook=lambda d: namedtuple("account", d.keys())(*d.values()))
    print credentials._asdict()
    try:
        # for credential in credentials:
        for server in get_vms(credentials.hq, "hq"):
            print server
    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
#if __name__ == "__main__":
#    main()
