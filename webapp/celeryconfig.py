from celery.schedules import crontab
import shelve

workertasks = {}
workers = []
shelf = shelve.open("endpoints.db")
for endpoint in shelf:
	workertasks[endpoint] = {
	'task' : 'workers.' + shelf[endpoint]['worker_script'] + '.task',
	'schedule' : crontab(minute="*")
	}
	workers.append('workers.'+ endpoint)

	


CELERY_IMPORTS = workers
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = workertasks


