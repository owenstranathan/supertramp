"""
Setting and constants for project
"""
import sys
import os
from logging.config import dictConfig
from pathlib import Path

# Constants
log_base: Path = Path(os.environ.get('LOG_BASE'))  # type: ignore

# Redis
redis: dict = {
    'host': os.environ.get('REDIS_HOST'),
    'port': int(os.environ.get('REDIS_PORT')),  # type: ignore
}

redis_url: str = f"redis://{redis['host']}:{redis['port']}"

# App
app_conf: dict = {}

# Celery
celery_conf: dict = {
    'broker': redis_url,
    'backend': redis_url
}

# Logging
log_conf = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': "[%(levelname)s] <%(name)s>: %(message)s",
        },
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['stdout'],
        'level': 'DEBUG',
    }
}

def make_logging():
    dictConfig(log_conf)