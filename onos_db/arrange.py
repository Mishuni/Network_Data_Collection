import json
import requests
import os
from config import CTRL_IP,CTRL_PORT,CTRL_ID,CTRL_PW
import glob

FILE_ROOT=os.getcwd()
log_folder=FILE_ROOT+"/log"

def main():
    # log 폴더 없으면 만들기
    if(not os.path.isdir(log_folder)):
        os.mkdir(log_folder)
    # 기존에 있던 log 파일들 다 없애기
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

    # host 와 mac 주소 저장
    host = {}
    for i in range(0, len(HOST_INFO)):
        ip = HOST_INFO[i]["ipAddresses"][0]
        ip = str(int(ip[ip.rfind(".")+1:]))
        host[HOST_INFO[i]["mac"]] = "H"+ip
    
    print(json.dumps(host, indent=4, sort_keys=True))

    # 각 switch들의 포트 별 연결된 host 이름 저장
    topo = {}
    for i in range(0, len(DEVICE_INFO)):
        info = {"name":"","ports":{}}
        switch = DEVICE_INFO[i]["id"]

        name = "S" + str(int(switch[3:],16))
        info['name']=name
        for j in range(0, len(HOST_INFO)):
            ip = HOST_INFO[j]["ipAddresses"][0]
            ip = str(int(ip[ip.rfind(".")+1:]))
            locations = HOST_INFO[j]["locations"]
            for l in range(0,len(locations)):
                if(locations[l]["elementId"]==switch):
                    info["ports"][locations[l]["port"]]="H"+ip
        topo[switch]=info

    # 각 switch들의 포트 별 연결된 switch 이름 저장
    for i in range(0, len(LINK_INFO)):
        src = LINK_INFO[i]["src"]
        dst = LINK_INFO[i]["dst"]

        name = "S" + str(int(dst["device"][3:],16))
        topo[src["device"]]["ports"][src["port"]]=name

    print(json.dumps(topo, indent=4, sort_keys=True))

    # 위에서 추출한 정보를 담는 파일들 생성
    with open("topology.json", "w") as json_file:
        json.dump(topo, json_file)

    with open("host_mac.json", "w") as f :
        json.dump(host, f)

    
if __name__=="__main__":
    main()