"""
Gunicorn configuration for AIAPad production deployment
"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for large file uploads
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/tmp/gunicorn_access.log"
errorlog = "/tmp/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "aiapad-backend"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
# user = "aiapad"  # Comentado para teste
# group = "aiapad"  # Comentado para teste
tmp_upload_dir = "/tmp"

# SSL (if needed)
# keyfile = "/etc/ssl/private/aiapad.key"
# certfile = "/etc/ssl/certs/aiapad.crt"

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/opt/aiapad/backend',
]

# Preload application for better performance
preload_app = True

# Worker process lifecycle
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting AIAPad backend server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading AIAPad backend server")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("AIAPad backend server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s", req.method, req.path)

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    worker.log.debug("%s %s - %s", req.method, req.path, resp.status_code)

