from webapp import app, celeryconfig
from celery import current_app
from celery.bin import worker

application = current_app._get_current_object()

worker = worker.worker(app=application)

options = {
    'broker': app.config['CELERY_BROKER_URL'],
    'loglevel': 'INFO',
    'traceback': True,
}

#app.run(host='0.0.0.0', port=80, debug=True)
worker.run(**options)

