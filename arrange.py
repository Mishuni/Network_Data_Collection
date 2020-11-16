# from databases import *
# from celery import Celery
import json
import requests
import os
#from celeryconfig_db import CTRL_IP,CTRL_PORT,CTRL_ID,CTRL_PW
from config import CTRL_IP,CTRL_PORT,CTRL_ID,CTRL_PW
import glob
#print(glob.glob("*.log"))
#print(os.getcwd())
FILE_ROOT=os.getcwd()
log_folder=FILE_ROOT+"/log"
# print(os.path.dirname(os.path.realpath(__file__)) )
def main():
    if(not os.path.isdir(log_folder)):
        os.mkdir(log_folder)

    for i in glob.glob(log_folder+"/*.log"):
        print(i)
        os.remove(i)

    ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/devices"
    result = requests.get(ONOS_URI, auth=(CTRL_ID,CTRL_PW))
    DEVICE_INFO = result.json()["devices"]
    ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/hosts"
    result = requests.get(ONOS_URI,auth=(CTRL_ID,CTRL_PW))
    HOST_INFO = result.json()["hosts"]
    ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/links"
    result = requests.get(ONOS_URI,auth=(CTRL_ID,CTRL_PW))
    LINK_INFO = result.json()["links"]

    # with open('devices.json') as json_file:
    #     DEVICE_INFO = json.load(json_file)["devices"]


    # with open('hosts.json') as json_file:
    #     HOST_INFO = json.load(json_file)["hosts"]


    # with open('links.json') as json_file:
    #     LINK_INFO = json.load(json_file)["links"]

    host = {}
    for i in range(0, len(HOST_INFO)):
        ip = HOST_INFO[i]["ipAddresses"][0]
        ip = str(int(ip[ip.rfind(".")+1:]))
        host[HOST_INFO[i]["mac"]] = "H"+ip
    
    print(json.dumps(host, indent=4, sort_keys=True))

    topo = {}
    for i in range(0, len(DEVICE_INFO)):
        info = {"name":"","ports":{}}
        switch = DEVICE_INFO[i]["id"]
        # if("a" in switch):
        #     name = "S10"
        # else:
        name = "S" + str(int(switch[3:],16))
        info['name']=name
        for j in range(0, len(HOST_INFO)):
            ip = HOST_INFO[j]["ipAddresses"][0]
            ip = str(int(ip[ip.rfind(".")+1:]))
            locations = HOST_INFO[j]["locations"]
            for l in range(0,len(locations)):
                if(locations[l]["elementId"]==switch):
                    info["ports"][locations[l]["port"]]="H"+ip # h3 h2 .. ?
        topo[switch]=info


    for i in range(0, len(LINK_INFO)):
        src = LINK_INFO[i]["src"]
        dst = LINK_INFO[i]["dst"]
        # if("a" in dst["device"]):
        #     name = "S10"
        # else:
        name = "S" + str(int(dst["device"][3:],16))
        #info['name']=name

        #name = "S" + str(int(dst["device"][3:]))
        topo[src["device"]]["ports"][src["port"]]=name

    print(json.dumps(topo, indent=4, sort_keys=True))

    with open("topology.json", "w") as json_file:
        json.dump(topo, json_file)

    with open("host_mac.json", "w") as f :
        json.dump(host, f)

    
if __name__=="__main__":
    # CTRL_IP = "172.17.0.3"
    # CTRL_PORT = "8181"
    # CTRL_ID = "onos"
    # CTRL_PW = "rocks"
    main()