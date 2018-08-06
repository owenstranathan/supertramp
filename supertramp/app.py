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


@app.route('/build/logs/<project_name>/<commit_id>', methods=['GET'])
def build_logs(project_name: str, commit_id: str):
    pass
    # log_path: Path = build_log_path_for(project_name, commit_id)
    # def stream_log():
    #     with log_path.open('r') as log_file:
    #         for line in log_file:
    #             yield line
    # return Response(stream_log(), mimetype='text/plain')


if __name__ == '__main__':
    app.run()