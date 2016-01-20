import multiprocessing
from os import getenv
bind = '0.0.0.0:5000'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 600
threads = multiprocessing.cpu_count() * 2
max_requests = 600
max_requests_jitter = 50
errorlog = '-'
accesslog = '-'
loglevel = 'warning'
# Read the DEBUG setting from env var
try:
    if getenv('BOOTSTRAP_DEBUG').lower() == 'true':
        loglevel = 'debug'
        debug = True
except:
    pass
