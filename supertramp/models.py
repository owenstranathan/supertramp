"""
Simple model classes to wrap redis hashes to store build information
"""
from __future__ import annotations

import datetime
from typing import (
    Any,
    Optional
)
from pathlib import Path

from walrus import (
    Database,
    Model,
    TextField,
    DateTimeField,
    JSONField
)

from .settings import log_base
from .utils import (
    project_id,
    build_id,
    deploy_id
)

db = Database()


class CustomModel(Model):

    @classmethod
    def get_one_or_none(cls, expr: Any) -> Optional[CustomModel]:
        try:
            return cls.get(expr)
        except ValueError:
            return None

    def __eq__(self, other: CustomModel) -> bool:  # type: ignore
        return self.__dict__ == other.__dict__

    def __ne__(self, other: CustomModel) -> bool:  # type: ignore
        return not self == other


class Project(CustomModel):
    __database__ = db
    name = TextField(index=True)
    org = TextField(index=True)
    id = TextField(primary_key=True)
    url = TextField(index=True)
    creation_date = DateTimeField(index=True, default=datetime.datetime.now)
    secrets = JSONField(default={})

    def __init__(self, *args, **kwargs) -> None:
        kwargs['id'] = project_id(kwargs['org'], kwargs['name'])
        super().__init__(*args, **kwargs)

    @property
    def full_name(self) -> str:
        """
        Munges org and name together to get a more unique name
        """
        return f"{self.org}/{self.name}"

    @property
    def log_path(self) -> Path:
        """
        Path to log_base/project.id
        """
        return log_base / self.id

    @property
    def builds(self) -> Any:
        """
        Returns a list of builds for this project ordered by their creation_date
        """
        return Build.query(Build.project_id == self.id, order_by=Build.creation_date)
    
    @property
    def deploys(self) -> Any:
        """
        Returns a list of deployments for this project ordered by their creation_date
        """
        return Deploy.query(Deploy.project_id == self.id, order_by=Deploy.creation_date)

    def build(self) -> None:
        """
        Trys to bulid the project and creates new build record
        """
        pass


class Build(CustomModel):
    __database__ = db
    id = TextField(primary_key=True)
    project_id = TextField(index=True)
    commit_id = TextField(index=True)
    branch = TextField(index=True)
    creation_date = DateTimeField(index=True, default=datetime.datetime.now)

    def __init__(self, *args, **kwargs) -> None:
        kwargs['id'] = build_id(kwargs['project_id'], kwargs['commit_id'])
        super().__init__(*args, **kwargs)

    @property
    def project(self) -> Project:
        """
        Returns the project this build is for
        """
        return Project.get(Project.id == self.project_id)

    @property
    def log_path(self) -> Path:
        """
        Path to self.project.log_path/self.id
        """
        return self.project.log_path / "builds" / self.id
    
    @property
    def logs(self) -> str:
        """
        Reads the contents of a build log
        """
        return self.log_path.open().read()

    @property
    def deploys(self) -> Any:
        """
        Returns a list of Deploys for this build ordered by their creation_date
        """
        return Deploy.query(Deploy.build_id == self.id, order_by=Deploy.creation_date)


class Deploy(CustomModel):
    __database__ = db
    id = TextField(primary_key=True)
    project_id = TextField(index=True)
    build_id = TextField(index=True)
    creation_date = DateTimeField(index=True, default=datetime.datetime.now)

    def __init__(self, *args, **kwargs) -> None:
        kwargs['id'] = deploy_id(kwargs['project_id'], kwargs['build_id'])
        super().__init__(*args, **kwargs)

    @property
    def build(self) -> Build:
        """
        Returns the build for this deployment
        """
        return Build.get(Build.id == self.build_id) 
    
    @property
    def project(self) -> Project:
        """
        Returns the project for this deployment
        """
        return Project.get(Project.id == self.project_id)

    @property
    def log_path(self) -> Path:
        """
        Path to self.project.log_path/deploys/self.id
        """
        return self.project.log_path / "deploys" / self.id
    