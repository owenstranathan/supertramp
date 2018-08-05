"""
Utilities for the project
"""
import logging
from typing import (
    List,
    Dict,
    Any
)
from pathlib import Path
import subprocess
import hashlib

from supertramp.settings import(
    BUILD_LOGS_DIR
)

logger = logging.getLogger(__name__)

build_logs_directory: Path = Path(BUILD_LOGS_DIR)


def parse_git_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    project_name: str = payload['repository']['full_name']
    commit_id:str = payload['head_commit']['id']
    ref: str = payload['ref']
    return {
        "project_name": project_name,
        "commit_id": commit_id,
        "repo_url": payload['repository']['url'],
        "branch": ref.split('/')[-1],
        "log_path": build_log_path_for(project_name, commit_id)
    }


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


def sha1(string: str) -> str:
    return hashlib.sha1(string.encode()).hexdigest()


def build_log_path_for(project_name, commit_id) -> Path:
    current_build_log_directory: Path = build_logs_directory / sha1(project_name)
    current_build_log_directory.mkdir(parents=True, exist_ok=True)
    return current_build_log_directory / commit_id


def clone_repo(repo_url: str, clone_to: str, branch: str, log_path: str) -> None:
    run(['git', 'clone', '-b', branch, repo_url, clone_to], log_path=Path(log_path))


def build_project(project_path: str, log_path: str) -> None:
    run(['make', 'build'], log_path=Path(log_path), cwd=project_path)    


def tell_slack(payload: dict) -> None:
    pass