"""
Utilities for the project
"""
import logging
import subprocess
import hashlib
from typing import (
    List,
    Dict,
    Any
)
from pathlib import Path

from flask import Flask
from celery import Celery

from .settings import (
    app_conf,
    celery_conf,
)

logger = logging.getLogger(__name__)


def run(args: List[str], log_path: Path = None, cwd: str=None) -> subprocess.CompletedProcess:
    proc = subprocess.run(args,
                          cwd=cwd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True)
    if log_path:
        with log_path.open('w') as log_file:
            for line in proc.stdout:
                log_file.write(line)
    else:
        logger.info(proc.stdout)
    proc.check_returncode()
    return proc


def sha1(string: str) -> str:
    return hashlib.sha1(string.encode()).hexdigest()


def project_id(org: str, name: str) -> str:
    return sha1(f"{org}/{name}")


def build_id(project_id: str, commit_id: str) -> str:
    return sha1(f"{project_id}/{commit_id}")


def deploy_id(project_id: str, build_id: str) -> str:
    return sha1(f"{project_id}/{build_id}")


def make_app():
    app = Flask(__name__)
    app.config.update(**app_conf)
    return app 


def make_celery(app):
    celery = Celery(
        app.import_name,
        **celery_conf,
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

