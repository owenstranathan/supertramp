
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .models import (
    Build,
    Deploy
)

class Event():
    listeners: List[Listener] = []  # pylint: disable=E0601

    def emit(self) -> None:
        for listener in self.listeners:
            listener.listen(self)

    @classmethod
    def subscribe(cls, listener: Listener) -> None:
        cls.listeners.append(listener)


class Listener():
    def listen(self, event: Event) -> None:
        pass


@dataclass 
class BuildCompletedEvent(Event):
    build: Build
    succeeded: bool 


@dataclass
class DeployCompletedEvent(Event):
    deploy: Deploy
    succeeded: bool
