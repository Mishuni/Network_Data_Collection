import datetime
import json
from arrange import main

CELERYBEAT_SCHEDULE = {
	'add-every-7-seconds':{
		'task':'task_mininet_db.ONOS_CELERY_TASK',
		'schedule':datetime.timedelta(seconds=5),
		'args':()
	}
}
CELERY_TIMEZONE='UTC'

main()
with open('topology.json') as json_file:
    topology = json.load(json_file)


with open('host_mac.json') as f:
    hosts = json.load(f)