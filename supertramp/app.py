from tempfile import TemporaryDirectory
from pathlib import Path

from flask import (
    Flask,
    request,
    Response,
    url_for
)

from supertramp.settings import (
    BUILD_LOGS_DIR,
    make_celery 
)
from supertramp.utils import (
    run,
    sha1,
    build_log_path_for,
    clone_repo,
    build_project,
    tell_slack
)


app = Flask(__name__)
# celery = make_celery(app)



@app.route('/build', methods=['POST'])
def build():
    """
    Checks out and builds the repository at 
    payload = request.get_json()
    repository_url = payload['repository_url']
    """
    _build(request.get_json())
    return Response('BEEP', 200)

@app.route('/build/logs/<project_name>/<commit_id>', methods=['GET'])
def build_logs(project_name: str, commit_id: str):
    log_path: Path = build_log_path_for(project_name, commit_id)
    def stream_log():
        with log_path.open('r') as log_file:
            for line in log_file:
                yield line
    return Response(stream_log(), mimetype='text/plain')


# @celery.task()
def _build(payload):
    breakpoint()
    project_name = payload['repository']['full_name']
    commit_id: str = payload['head_commit']['id']
    repo_url: str = payload['repository']['url']
    ref: str = payload['ref']
    branch: str = ref.split('/')[-1]
    log_path: Path = build_log_path_for(project_name, commit_id)
    with TemporaryDirectory() as tmpd:
        try:
            clone_repo(repo_url, tmpd, branch, log_path=log_path)
            build_project(tmpd, log_path)
            payload['build'] = {
                'success': True,
                'log': url_for('build_logs', project_name=project_name, commit_id=commit_id)
            }
            tell_slack(payload)
        except Exception as ex:
            breakpoint()
            print(ex)
            raise ex

if __name__ == "__main__":
    app.run()