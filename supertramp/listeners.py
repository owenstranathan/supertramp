from .events import (
    Event,
    Listener
)


class SlackListener(Listener):
    def listen(self, event: Event) -> None:
        pass
