from typing import Callable
import abc
import logging

import sdl2

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


class Events:
    event_handlers = {}

    @staticmethod
    def handle_events():
        for event in sdl2.ext.get_events():
            listeners = Events.event_handlers.get(event.type, [])
            for listener in listeners:
                listener(event)

    @staticmethod
    def add_listener(event_type : str, listener : Callable[[sdl2.SDL_Event], None]):
        if not listener or not event_type:
            return

        event_id = sdl2.__dict__.get(event_type)
        if type(event_id) is int :
            if event_id not in Events.event_handlers:
                Events.event_handlers[event_id] = []
            Events.event_handlers[event_id].append(listener)
        else:
            raise ValueError(f"No event id to the event type {event_type}, see: https://wiki.libsdl.org/SDL_Event")

