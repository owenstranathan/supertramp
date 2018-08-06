from pathlib import Path

from flask import (
    Flask,
    request,
    Response,
    url_for
)

import supertramp.tasks as tasks
from .settings import (
    app_conf,
)
from .utils import (
    project_id,
    build_id,
    deploy_id,
)
from .models import (
    Build,
    Deploy,
)

app = Flask(__name__)
app.config.update(**app_conf)



@app.route('/build', methods=['POST'])
def build():
    """
    Checks out and builds the repository at 
    payload = request.get_json()
    repository_url = payload['repository_url']
    """
    tasks.build.s(request.get_json()).apply_async()
    return Response('BEEP', 200)


def log_responder(log_path: Path):
    def stream_log():
        with log_path.open('r') as log_file:
            for line in log_file:
                yield line
    return Response(stream_log(), mimetype='text/plain')


@app.route('/build/logs/<org>/<name>/<commit_id>', methods=['GET'])
def build_logs(org: str, name: str, commit_id: str):
    build = Build.get_one_or_none(Build.commit_id == commit_id and Build.project_id == project_id(org, name))
    if not build:
        return Response('404 Not Found', 404)
    return log_responder(build.log_path)

@app.route('/deploy/logs/<org>/<name>/<commit_id>', methods=['GET'])
def deploy_logs(org: str, name: str, commit_id: str):
    id = deploy_id(project_id(org, name), build_id(project_id(org, name), commit_id))
    deploy = Deploy.get_one_or_none(Deploy.id == id)
    if not deploy:
        return Response('404 Not Found', 404)
    return log_responder(deploy.log_path)


if __name__ == '__main__':
    app.run()