from __future__ import print_function
import sys
import libvirt
import lxml.etree as le
from xml.dom import minidom
import collections
from time import sleep
#from xlrd import open_workbook
from xml.dom.minidom import parse
import paramiko

vm_list = []
vm_map = {}
vm_IP = collections.defaultdict(list)
vm_MAC = collections.defaultdict(list)

uniq_MAC = set()
uniq_IP = set()
vm_same_mac = []
vm_same_ip = []

# Support for multiple hypervisors
hyp_list = []
hyp_list.append('152.14.83.161')
hyp_vm_map = {}
hyp_vm_IP = collections.defaultdict(list)
hyp_vm_MAC = collections.defaultdict(list)
hyp_vm_same_mac = []
hyp_vm_same_ip = []
hyp_username = collections.defaultdict(list)
hyp_pwd = collections.defaultdict(list)


# Open connection
#conn = libvirt.open('qemu:///system')
#if conn == None:
#  print ("Connection open failed to qemu:///system")
#  exit(1)

# List all active domains
def list_active_domains(conn):
  domIDs = conn.listDomainsID()
  if domIDs == None:
    print ("Failed to list all active domains")

  if len(domIDs) == 0:
    print("No active domains")

  else:
    for domId in domIDs:
      dom = conn.lookupByID(domId)
      if dom == None:
        print ("Failed to open connection to domain")
      else:
        vm_list.append(dom)   # Creating a list of VM IDs

# Retrieving the MAC address of all the interfaces of running VMs
def retrive_macs():
  for vmID in vm_list:
    dom_xml = minidom.parseString(vmID.XMLDesc(0))
    #dom_xml = parse(vmID.XMLDesc(0))
    iface_type = dom_xml.getElementsByTagName('interface')
    tag_name = dom_xml.getElementsByTagName('name')
    vm_name = tag_name[0].firstChild.nodeValue
    vm_map[vmID] = vm_name

    for iface in iface_type:
      tag_mac = iface.getElementsByTagName('mac')
      mac_addr = tag_mac[0].getAttribute('address')
      vm_MAC[vm_name].append(mac_addr)


# Retrieving the IP addresses of all the interfaces of running VMs
def retrive_ips(conn):
  for vmID in vm_list:
     iface = vmID.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE,0)
     if iface is not None:
       for (name,value) in iface.iteritems():
         if value['addrs']:
           for ipaddr in value['addrs']:
            if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
               if ipaddr['addr'] != '127.0.0.1':
                 vm_IP[vm_map[vmID]].append(ipaddr['addr'])


# Listing all the MAC and IP addresses of all the interfaces of the running VM
def dump_mac_ip():
  for hyp in hyp_list:
    for name in hyp_vm_MAC[hyp]:
      print ("Domain: " + name)
      if name in hyp_vm_IP[hyp]:
        for ip in hyp_vm_IP[hyp][name]:
          print ("IP: " + ip)
      for mac in hyp_vm_MAC[hyp][name]:
        print ("MAC: " + mac)
      print ("\n")



if __name__ == "__main__":
  input_string = raw_input("Enter list of comma separated hypervisor IPs\n")
  hyp_list = input_string.split()

  for hypervisor in hyp_list:
    input_string = raw_input("Enter username for " + hypervisor + ": ")
    hyp_username[hypervisor] = input_string.split()
    input_string = raw_input("Enter password for " + hypervisor + ": ")
    hyp_pwd[hypervisor] = input_string.split()

  for hyp in hyp_list:
    conn = libvirt.open('qemu:///system')
    if conn is None:
      print ("Connection open failed to qemu:///system")
      exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    username = hyp_username[hyp]
    password = hyp_pwd[hyp]
    client.connect(hyp, hyp_username=username, password=password)
    
    list_active_domains(conn)
    retrive_macs()
    retrive_ips(conn)
    #dump_mac_ip()

    hyp_list[hyp] = vm_list
    hyp_vm_MAC[hyp] = vm_MAC
    hyp_vm_IP[hyp] = vm_IP

    dump_mac_ip()

  # Identifying unique and duplicate MAC addresses
  # across multiple hypervisors
  for hyp in hyp_vm_MAC:
    for vm in hyp_vm_MAC[hyp]:
      for mac in hyp_vm_MAC[hyp][vm]:
        if mac in uniq_MAC:
          vm_same_mac.append(vm,mac)
          hyp_vm_same_mac.append(hyp,vm,mac)
        uniq_MAC.add(mac)


  # Identifying unique and duplicate IP addresses
  # across multiple hypervisors
  for hyp in hyp_vm_IP:
    for vm in hyp_vm_IP[hyp]:
      for ip in hyp_vm_IP[hyp][vm]:
        if ip in uniq_IP:
          vm_same_ip.append(vm,ip)
          hyp_vm_same_ip.append(hyp,vm,ip)
        uniq_IP.add(ip)


  # Listing all conflicting MAC addresses
  for conf in vm_same_mac:
     print ("Conflicting MAC addresse between " + conf[0] + "and " + conf[1])

  # Listing all conflicting MAC address of VMs in a hypervisor
  for hyp_conf in hyp_vm_same_mac:
    print ("Conflicting MAC addresses in hypervisor " + hyp_conf[0] + "for the VM " + hyp_conf[1] + "with MAC " + hyp_conf[2])
    
  # Resolve identified MAC/IP conflicts
  vm_MAC = collections.defaultdict(list)
  for conf in vm_same_mac:
     vm_MAC[conf[0]].append(conf[1])

  if len(vm_same_mac) == 0:
    print ("There are no conflicting MAC and IP addresses")
    #exit(1)

  else:
    print ("Identified MAC/IP conflicts")

  client.close()
  
