from .events import (
    Event,
    BuildCompletedEvent,
    Listener
)


class SlackListener(Listener):
    def listen(self, event: Event) -> None:
        if isinstance(event, BuildCompletedEvent):
            print(f"Build {event.build.id} completed")
            print(event.build.logs)