# -*- coding: utf-8 -*- 
from databases import *
from celery import Celery
import json
import requests
import os
from celeryconfig_db import topology
from config import BROKER_CONF,CTRL_IP, CTRL_PORT, CTRL_ID, CTRL_PW,PORT_MES

# Broker addr
# example ) 'amqp://sdn:sdn@172.17.0.2:5672/'
broker_http = 'amqp://'+BROKER_CONF['bro_id']+":"+BROKER_CONF['bro_pw']+"@"+BROKER_CONF['bro_ip']+":"+BROKER_CONF['bro_port']+"/"
#Broker(RabbiMQ) setting
app = Celery('ONOS_TASK', broker=broker_http)
#celeryconfig.py 에 정의한 celery task 환경설정 정보 가져오기
app.config_from_object('celeryconfig_db')
FILE_ROOT=os.getcwd()
log_folder=FILE_ROOT+"/log"

#Celery를 통해 실행시켜줄 ONOS TASK "ONOS_CELERY_TASK"함수 정의
#반드시 @app.taks아래에 함수 작성
@app.task
def ONOS_CELERY_TASK():
    try:
        #ONOS REST API를 통해 ONOS와 연결된 스위치 정보(스위치 DPID)가져오기
        ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/devices"
        result = requests.get(ONOS_URI, auth=(CTRL_ID,CTRL_PW))
        DEVICE_INFO = result.json()["devices"]
        #ONOS REST API를 통해 앞에서 조회한 스위치 DPID별 Port상태 조회
        ONOS_URI = "http://" + CTRL_IP + ":" + CTRL_PORT + "/onos/v1/statistics/ports"
        result = requests.get(ONOS_URI,auth=(CTRL_ID,CTRL_PW))
        
        #device(switch, router, ap)별로 수행
        for i in range(0, len(DEVICE_INFO)):
            SW_DPID = DEVICE_INFO[i]["id"]
            SW_STATE_INFO = result.json()["statistics"]

            #ONOS REST API를 통해 ONOS와 연결된 모든 스위치의 포트별
            for j in range(0, len(SW_STATE_INFO)):
                if SW_STATE_INFO[j]["device"] == SW_DPID:
                    SW_NAME = topology[SW_DPID]["name"]
                    PORT_STATE = SW_STATE_INFO[j]["ports"]
                    for k in range(0, len(PORT_STATE)):
                        MATCH_PORT = PORT_STATE[k]["port"]
                        #PORT_NAME = "H" + str(MATCH_PORT)
                        PORT_NAME = topology[SW_DPID]["ports"][str(MATCH_PORT)]
                        CURRENT_RX_BYTE_COUNT = float(PORT_STATE[k]["bytesReceived"])
                        CURRENT_TX_BYTE_COUNT = float(PORT_STATE[k]["bytesSent"])
                        CURRENT_DURATION_TIME = float(PORT_STATE[k]["durationSec"])
                        packetsRxDropped = PORT_STATE[k]["packetsRxDropped"]
                        packetsTxDropped = PORT_STATE[k]["packetsTxDropped"]
                        FILE_NAME = "dpid_" + SW_DPID.replace(":","") + "_port_" + str(MATCH_PORT)
                        FILE_DIR = log_folder+"/"+FILE_NAME+".log"
                        #처음이거나 이전에 측정된 3개의 파라미터가 저장된 파일이 없다면 파일로 저장
                        if j==0 or os.path.exists(FILE_DIR) == False:
                            data = str(CURRENT_TX_BYTE_COUNT) + "_" + str(CURRENT_RX_BYTE_COUNT) + "_" + str(CURRENT_DURATION_TIME)
                            FILE_WRITE(FILE_DIR,data)
                        #이전 파일이 있다면, 파일을 읽어 이전 저장값 가져오기
                        else:
                            DATA = FILE_READ(FILE_DIR)
                            DATA = DATA.split("_")
                            PREVIOUS_TX_BYTE_COUNT = float(DATA[0])
                            PREVIOUS_RX_BYTE_COUNT = float(DATA[1])
                            PREVIOUS_DURATION_TIME = float(DATA[2])
                            data = str(CURRENT_TX_BYTE_COUNT) + "_" + str(CURRENT_RX_BYTE_COUNT) + "_" + str(CURRENT_DURATION_TIME)
                            FILE_WRITE(FILE_DIR, data)

                            #이전과 현재 측정된 Duration time의 차이가 0인 경우
                            #SDN제어기가 아직 스위치 포트 상태 정보를 갱신하지 못한 것이므로(이전과 동일)
                            #송수신 트래픽처리량을 계산할 수 없음
                            #SDN제어기가 갱신하지 못했음을 메세지로 출력
                            if CURRENT_DURATION_TIME - PREVIOUS_DURATION_TIME == 0 :
                                p_statement = "The SDN controlelr has not updated The Port No." + str(MATCH_PORT) + "State!!"
                                print(p_statement)
                            else:
                                TX_DIFF = CURRENT_TX_BYTE_COUNT - PREVIOUS_TX_BYTE_COUNT
                                RX_DIFF = CURRENT_RX_BYTE_COUNT - PREVIOUS_RX_BYTE_COUNT
                                TX_THROUGHPUT = TX_DIFF*8/(CURRENT_DURATION_TIME - PREVIOUS_DURATION_TIME)
                                RX_THROUGHPUT = RX_DIFF*8/(CURRENT_DURATION_TIME - PREVIOUS_DURATION_TIME)
                                TX_THROUGHPUT = round(TX_THROUGHPUT,4)
                                RX_THROUGHPUT = round(RX_THROUGHPUT,4)
								#print("test1")

                                json_body=[
                                    {
                                        "measurement":PORT_MES,
                                        "tags":{
                                            "port":MATCH_PORT,
                                            "port_name":PORT_NAME,
                                            "device":SW_NAME
                                        },
                                        "fields":{
                                            "rx_byte_count":CURRENT_RX_BYTE_COUNT,
                                            "tx_byte_count":CURRENT_TX_BYTE_COUNT,
                                            "duration_time":CURRENT_DURATION_TIME,
                                            "packetsRxDropped":packetsRxDropped,
                                            "packetsTxDropped":packetsTxDropped,
                                            "tx_throughput":TX_THROUGHPUT,
                                            "rx_throughput":RX_THROUGHPUT,
                                            "tx_byte_diff":TX_DIFF, 
                                            "rx_byte_diff":RX_DIFF,
                                        }
                                    }
                                ]

                                DB_INSERT = InfluxDB_InsertData(json_body)
                                
                                if(DB_INSERT):
                                    print ("Insert Complete!!")
                                    
    except Exception as error:
        print("ERROR:",error)
