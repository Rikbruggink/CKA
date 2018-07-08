#!/usr/bin/env python

'''A Dynamic inventory source for Ansible.

Gets a list of running VirtualBox VMs and returns it as a JSON structure.

Caveats:
 * Only running VMs are listed
 * Only the first IP address is listed
 * Guest additions need to be installed

Reading:
 * http://docs.ansible.com/intro_inventory.html
 * http://docs.ansible.com/developing_inventory.html
'''
import json
import sys
from copy import copy
from subprocess import Popen, PIPE
from argparse import ArgumentParser

HOSTVAR_TEMPLATE = {'ansible_ssh_user': 'root','ansible_python_interpreter': '/usr/bin/python3'}
VBOX_GROUP = 'vbox'

def get_running_vm_names():
    '''Returns an iterable of VM name strings'''
    vmlist = Popen(['VBoxManage', 'list', 'runningvms'], stdout=PIPE, stderr=PIPE)
    sout, serr = vmlist.communicate()
    if serr != '' or vmlist.returncode != 0:
        raise UserWarning(serr)
    for line in sout.splitlines():
        yield line.split()[0].strip('"')
        
def get_hostvars(vmname):
    '''Gets data for an individual VM and returns it as a dictionary.
    
    The primary (currently only) dynamic item is ansible_ssh_host, which is obtained
    from VirtualBox's first interface entry. Modify HOSTVARS_TEMPLATE to add static
    host vars.
    '''
    hostvars = copy(HOSTVAR_TEMPLATE)
    cmd = Popen(['VBoxManage', 'guestproperty', 'get', vmname,
                 '/VirtualBox/GuestInfo/Net/0/V4/IP'], stdout=PIPE, stderr=PIPE)
    sout, serr = cmd.communicate()
    if serr != '' or cmd.returncode != 0:
        raise UserWarning('VBoxManage error: %s' % serr)
    if sout != '':
        hostvars['ansible_ssh_host'] = sout.split()[-1].strip()
    return hostvars

def vm_list_as_json():
    '''Create JSON string containing host data'''
    hostlist = []
    hostvars = {}
    for vmname in get_running_vm_names():
        hostlist.append(vmname)
        hostvars[vmname] = get_hostvars(vmname)
    return json.dumps({VBOX_GROUP: hostlist, '_meta': {'hostvars': hostvars}})

def main():
    '''Command line parsing

    The --list option is used by Ansible to fetch the host list; We include host
    data in the host list, but also support fetching it individually with --host.
    '''
    parser = ArgumentParser(usage='%(prog)s --list')
    parser.add_argument('--list', action='store_true', default=False,
                        help='return VM list with host data')
    parser.add_argument('--host', dest='vmname', help='return host data')
    args = parser.parse_args()
    try:
        if args.list:
            print vm_list_as_json()
        elif args.vmname is not None:
            print json.dumps(get_hostvars(args.vmname))
        else:
            parser.print_help()
    except UserWarning, exc:
        sys.stderr.write(exc.message)
        sys.exit(1)

if __name__ == '__main__':
    main()
