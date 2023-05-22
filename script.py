import paramiko
import time
import getpass
import os
import json
import sys,subprocess
from subprocess import Popen, PIPE



CTRL_Y = '\x19'
WINDOWS_LINE_ENDING = '\r\n'
UNIX_LINE_ENDING = '\n'



def runhost(_ip,_UN,_PW):    
    # logfile
    f = open('sshlogfile0001.txt', 'a')
    twrssh = paramiko.SSHClient()
    twrssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        twrssh.connect(_ip, port=22, username=_UN, password=_PW, timeout= 10)
        remote = twrssh.invoke_shell()
    except:
        print("ERROR !!!!! ------------->>> connection to host failed...")
        return   #exit the function 
    
    for command in host['commands']:
        
        s = command.replace("$NEW_VLAN_ID",NEW_VLAN_ID)
        s = s.replace("$NEW_VLAN_ISID",NEW_VLAN_ISID)
        s = s.replace("$NEW_VLAN_NAME",NEW_VLAN_NAME)
        s = s.replace("$NEW_VLAN_FIREWALL_IFALIAS",NEW_VLAN_FIREWALL_IFALIAS)
        s = s.replace("$NEW_VLAN_FIREWALL_ADDRESS",NEW_VLAN_FIREWALL_ADDRESS)
        s = s.replace("$NEW_VLAN_FIREWALL_IP",NEW_VLAN_FIREWALL_IP)
        s = s.replace("$NEW_VLAN_FIREWALL_SUBNET",NEW_VLAN_FIREWALL_SUBNET)
        s = s.replace("$NEW_VLAN_FIREWALL_SNMASK",NEW_VLAN_FIREWALL_SNMASK)
        s = s.replace("$FIREWALL_ZONE_FN",FIREWALL_ZONE_FN)
        s = s.replace("$FIREWALL_ZONE_TT",FIREWALL_ZONE_TT)
        s = s.replace("$NEW_VLAN_VMNET_NAME",NEW_VLAN_VMNET_NAME)

        print(f"running command: {s}")            

        if s == "CTRL_Y":
            remote.send(CTRL_Y)
        else: 
            
            
            remote.send(' %s \n' % s)
            time.sleep(3)
            buf = remote.recv(65000)
            s = str(buf) 
            text = s.replace("\\r\\n", "\r")
            text = text.replace("\\r", "")
            f.write(text)
            print (text) 

    twrssh.close()
    f.close()


#### Main programm starts here


with open('hosts.json', 'r') as file:
    hosts = json.load(file)['hosts']
with open('hosts.json', 'r') as file:        
    vlan_info = json.load(file)['VLAN']


# currentSystype stores the current system type - if changed in the next loop new credentials are required
currentSystype = "init"

NEW_VLAN_NAME = vlan_info['NEW_VLAN_NAME']
NEW_VLAN_ID = vlan_info['NEW_VLAN_ID']
NEW_VLAN_ISID = vlan_info['NEW_VLAN_ISID']
NEW_VLAN_FIREWALL_ADDRESS = vlan_info['NEW_VLAN_FIREWALL_ADDRESS']
NEW_VLAN_FIREWALL_IFALIAS = vlan_info['NEW_VLAN_FIREWALL_IFALIAS']
NEW_VLAN_FIREWALL_IP = vlan_info['NEW_VLAN_FIREWALL_IP']
NEW_VLAN_FIREWALL_SUBNET = vlan_info['NEW_VLAN_FIREWALL_SUBNET']
NEW_VLAN_FIREWALL_SNMASK = vlan_info['NEW_VLAN_FIREWALL_SNMASK']
FIREWALL_ZONE_FN = vlan_info['FIREWALL_ZONE_FN']
FIREWALL_ZONE_TT = vlan_info['FIREWALL_ZONE_TT']
NEW_VLAN_VMNET_NAME = vlan_info['NEW_VLAN_VMNET_NAME']


print (NEW_VLAN_NAME)
print (NEW_VLAN_ID)



for host in hosts:
    enabled = {host['enabled']}
    systype = host['systype']
    ips =  str(host['name'])

    
    #print(f"Next system: {ip}, {systype}")
    
    if enabled == {False}:        
        print(f"Host/s {ips} is disabled in config - {systype}")
    elif enabled == {True}:  
        for ip in host['name']:
            print(f"Host {ip} is enabled in config - {systype}")            
            proceedHost = input("do you want to proceed? [ENTER] = go | [n] = no : ")  
            if proceedHost != "n":            
                if systype != currentSystype and systype != 'vmware':
                    print("new systemtype requires new credentials. Pleasy input...")
                    UN = input("Username : ")        
                    PW = getpass.getpass("Password : ")
                    currentSystype = systype
                    runhost(ip,UN, PW)
                elif systype != currentSystype and systype == 'vmware':
                    print("external vmware script called ------>>>  please provide credentials if asked...")
                    p = subprocess.Popen(["powershell.exe", 
                    ".\\vSphere.ps1", ip, NEW_VLAN_ID, NEW_VLAN_VMNET_NAME], 
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)           
                    output, err =  p.communicate()
            
                    resOut = str(output)
                    resOut = resOut.replace("\\r\\n", "\r")
                    resOut = resOut.replace("\\n", "\r")
                    resOut = resOut.replace("\\r", "")

                    resErr = str(err)
                    resErr = resErr.replace("\\r\\n", "\r")
                    resErr = resErr.replace("\\n", "\r")
                    resErr = resErr.replace("\\r", "")

                    print(resOut)
                    print(resErr)
                    f = open('sshlogfile0001.txt', 'a')
                    f.write(str(resOut))
                    f.write(str(resErr))
                    f.close            
                    currentSystype = systype
            
                else:
                    runhost(ip,UN, PW)        
            else:
                print("host was skipped...")

