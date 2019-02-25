import celery

@celery.task()
def task():
	logger = task.get_logger()
	logger.info("scorecard")
