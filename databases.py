# -*- coding: utf-8 -*- 
from influxdb import InfluxDBClient
from config import DB_HOST,DB_PORT,DB_USER,DB_PSWD,DB_NAME
#ONOS REST API를 통해 조회된 정보를 파일로 저장하기 위한 함수
def FILE_WRITE(file_dir,data):
	f=open(file_dir,'w')
	f.write(data)
	f.close

#파일로 저장된, ONOS REST API를 통해 조회된 정보를 읽어오기
def FILE_READ(file_dir):
	f=open(file_dir,'r')
	data=f.readline()
	f.close()
	return data

#influxDB에 스위치 DPID, 포트번호, 송/수신 트래픽 처리량을 저장하는 함수
def InfluxDB_InsertData(json_body ):
	
	client = InfluxDBClient(DB_HOST,DB_PORT,DB_USER, DB_PSWD, DB_NAME)
	p_write = "Write points: {0}" + format(json_body)
	print(p_write)
	return client.write_points(json_body)


#influxDB에 스위치 DPID, 포트번호, 송/수신 트래픽 처리량을 저장하는 함수
def InfluxDB_InsertFlow( json_body ):
	
	client = InfluxDBClient(DB_HOST,DB_PORT,DB_USER, DB_PSWD, DB_NAME)
	#p_write = "Write points: {0}" + format(json_body)
	#print(p_write)
	return client.write_points(json_body)

def select_flow(flow_id,MEASUREMENT):
	sql = "select id,life from "+MEASUREMENT+" where id='"+flow_id+"'"
	
	client = InfluxDBClient(DB_HOST,DB_PORT,DB_USER, DB_PSWD, DB_NAME)
	result = client.query(sql)
	#print(result)
	try:
		return result.raw["series"][0]["values"]
	except:
		return {}
	