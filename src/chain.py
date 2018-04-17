"""
This module is attempt to overcomplicate things. I hope that successfull

Contains definition of ModuleChain class, which tries to handle module
management in clever way."""

from collections import deque

class ModuleChain(deque):
    """Stores callbacks to modules and when given event call callbacks for each
    module, until one can process this event. Modules can change
    events(transform current), delete or create new ones"""
    def process_event(self, data: dict) -> dict:
        """Process given event. If no module can process this event, event is
        returned"""
        pass
