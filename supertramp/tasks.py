import subprocess
import logging

from celery import Celery

from .utils import (
    run,
    project_id,
    build_id,
    deploy_id
)
from .models import (
    Project,
    Build
)

from .events import (
    BuildCompletedEvent
)
from .settings import (
    celery_conf,
    make_logging
)

make_logging()
logger = logging.getLogger(__name__)

celery = Celery(__name__, **celery_conf)


@celery.task(name=f"{__name__}.build")
def build(payload):
    org, name = payload['repository']['full_name'].split('/')
    url: str = payload['repository']['url']
    commit_id: str = payload['head_commit']['id']
    ref: str = payload['ref']
    branch: str = ref.split('/')[-1]

    project = Project.get_one_or_none(Project.id == project_id(org, name))
    if not project:
        project = Project.create(name=name, org=org, url=url)

    build = Build.get_one_or_none(Build.id == build_id(project.id, commit_id))
    if not build:
        build = Build.create(project_id=project.id, commit_id=commit_id, branch=branch)

    try:
        run(["supertramp", "-cb", branch,
                    "-l", str(build.log_path),
                    "-r", commit_id, 
                    "-m", "build", project.url])
        logger.info(f"Build {build.id}({project.full_name}@{build.branch}/{build.commit_id}) succeeded")
        success: bool = True
    except subprocess.CalledProcessError as ex:
        logger.exception(ex)
        logger.error(f"Build {build.id}({project.full_name}@{build.branch}/{build.commit_id}) failed")
        success: bool = False

    BuildCompletedEvent(build=build, succeeded=success).emit()


@celery.task()
def deploy(payload):
    # TODO: deploy things, use a redis to get shit and stuff
    pass