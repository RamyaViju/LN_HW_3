#################################################################################
# A python script to list all MAC and IP addresses of all ifaces of running VMs #
# and also resolve all IP and MAC conflicts and update the VM configuration.    #
#                                                                               #
# Execution: python q1.py                                                       #
#                                                                               #
#                                                                               #
# Authors: Ramya Vijayakumar (rvijaya4)                                         #
#          Prashanth Mallyampatti (pmallya)                                     #
#                                                                               #
#################################################################################

from __future__ import print_function
import sys
import libvirt
import lxml.etree as le
from xml.dom import minidom
import collections
from time import sleep
#from xlrd import open_workbook
from xml.dom.minidom import parse

vm_list = []
vm_map = {}
vm_IP = collections.defaultdict(list)
vm_MAC = collections.defaultdict(list)

uniq_MAC = set()
uniq_IP = set()
vm_same_mac = []
vm_same_ip = []

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
  for name in vm_MAC:
    print ("Domain: " + name)
    if name in vm_IP:
      for ip in vm_IP[name]:
        print ("IP: " + ip)
    for mac in vm_MAC[name]:
      print ("MAC: " + mac)
    print ("\n")


if __name__ == "__main__":
  conn = libvirt.open('qemu:///system')
  if conn is None:
    print ("Connection open failed to qemu:///system")
    exit(1)

  list_active_domains(conn)
  retrive_macs()
  retrive_ips(conn)
  dump_mac_ip()
  
    # Identifying unique and duplicate MAC addresses
  for vm in vm_MAC:
    for mac in vm_MAC[vm]:
      if mac in uniq_MAC:
        vm_same_mac.append(vm,mac)
      else:
        uniq_MAC.add(mac)


  # Identifying unique and duplicate IP addresses
  for vm in vm_IP:
    for ip in vm_IP[vm]:
      if ip in uniq_IP:
        vm_same_ip.append(vm,ip)
      else:
        uniq_IP.add(ip)


  # Listing all conflicting MAC addresses
  for conf in vm_same_mac:
     print ("Conflicting MAC addresse between " + conf[0] + "and " + conf[1])

  # Resolve identified MAC/IP conflicts
  vm_MAC = collections.defaultdict(list)
  for conf in vm_same_mac:
     vm_MAC[conf[0]].append(conf[1])

  if len(vm_same_mac) == 0:
    print ("There are no conflicting MAC and IP addresses")
    #exit(1)

  else:
    print ("Resolving MAC/IP conflicts")
    for vm in vm_MAC:
      dom = conn.lookByName(vm)
      dom.shutdown()
      dom.destroy()

      data = ""
      path = "/etc/libvirt/qemu/"+vm+".xml"
      with open(path, 'r') as fd:
        file_to_edit = le.parse(fd)
        for ele in file_to_edit.xpath('//*[attribute::address]'):
          if ele.attrib['address'] in macs:
            ele.attrib.pop('address')
            parent = ele.getparent()
            parent.remove(ele)
        data = le.tostring(file_to_edit)
      fd = open(path, 'w')
      fd.write(data)
      fd.close()

      # Create the VM with updated info
      dom = conn.createXML(data, 0)
      if dom is None:
        print ("Unable to define domian")
        exit(1)

    sleep(20)

    conn = libvirt.open('qemu:///system')
    if conn is None:
      print ("Connection open failed to qemu:///system")
      exit(1)

    list_active_domians(conn)
    retrive_macs()
    retrive_ips()

    print ("The MAC/IP list after conflict resolution is as follows:")
    dump_mac_ip()
