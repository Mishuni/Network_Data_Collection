from databases import *
from celery import Celery
import json
import requests
import os
from config import CTRL_IP,CTRL_PORT,CTRL_ID,CTRL_PW,FLOW_MES
from celeryconfig_db import topology, hosts
import time as tt

MEASUREMENT = FLOW_MES
# http://172.17.0.3:8181/onos/v1/flows
ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/flows"
print(ONOS_URI)

def flow_main():
    while True:
        result = requests.get(ONOS_URI,auth=(CTRL_ID,CTRL_PW))
        FLOW_INFO = result.json()["flows"]
        #print(json.dumps(FLOW_INFO, indent=4, sort_keys=True))
        for flow in FLOW_INFO:
            flow_id = flow["id"]
            state = flow["state"]
            if(state=="PENDING_ADD"):
                continue
            # time, id, life
            already = select_flow(flow_id,MEASUREMENT)
            #print(already)
            #print(len(already))
            time = ""
            if(len(already)>0):
                time =already[0][0]
                print(time)
            switch = topology[flow["deviceId"]]["name"]
            instructions = flow["treatment"]["instructions"][0]
            
            src=""
            dest="CONTROLLER"
            outport="CONTROLLER"
            inport=""

            if (flow["appId"]!="org.onosproject.core"):
                outport=topology[flow["deviceId"]]["ports"][str(instructions["port"])]
                info=flow["selector"]["criteria"]
                inport= topology[flow["deviceId"]]["ports"][str(info[0]["port"])]
                dest=hosts[info[1]["mac"]]
                src=hosts[info[2]["mac"]]

            print(src,dest,inport,outport)

            json_body=[
                {
                    "measurement":MEASUREMENT,
                    "tags":{
                        "id":flow_id,
                        "switch":switch,
                        "state":flow["state"],
                        "src":src,
                        "dest":dest,
                        "inport":inport,
                        "outport":outport
                    },
                    "fields":{
                        "life":flow["life"],
                        "lastSeen":flow["lastSeen"],
                        "packets":flow["packets"],
                        "bytes":flow["bytes"]
                    }
                }
            ]
            if time!="":
                json_body[0]["time"]=time
            #print(json_body)
            InfluxDB_InsertFlow(json_body)
        tt.sleep(2)


if __name__=="__main__":
    flow_main()