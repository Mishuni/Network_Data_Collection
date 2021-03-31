CTRL_IP = "172.17.0.3"  # onos container ip address
CTRL_PORT = "8181"      # onos api port number
CTRL_ID = "onos"        # onos id
CTRL_PW = "rocks"       # onos password

DB_HOST = "127.0.0.1"   # influxDB ip address
DB_PORT = "8086"        # influxDB port number
DB_USER = "admin"       # influxDB user name     (default)
DB_PSWD = "admin"       # influxDB user password (default)
DB_NAME = "sdn"         # influxDB database name

BROKER_CONF = {
	'bro_ip':'172.17.0.2',  # rabbitmq container ip address
	'bro_port':'5672',      # rabbitmq port number
	'bro_id':'sdn',         # rabbitmq id
	'bro_pw':'sdn'          # rabbitmq password
}

PORT_MES = "test"           # table name for data of hosts in influxDB 
FLOW_MES = "flow"           # table name for data of flows in influxDB