# coding: utf-8
from pyvcd import vcdirector
vcd = vcdirector("https://vcd.nxus.com/api")
vcd.init_session("jhchoi", "infosec", "chlwhdgkrrladlsgP%43")
print vcd.orgs()
vms = vcd.virtualmachines(vm_name="secindx")
for vm in vms:
    print vm['name']
    print vcd.network(vm['href'])
