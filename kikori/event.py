import logging
from typing import List, Callable, Dict

import sdl2

logger = logging.getLogger(__name__)


# Executes the wrapped function only if the event type matches.
def event_handler(event_type, union_key, predicate):
    def wrap(handler):
        def wrapped_handler(event):
            union_element = getattr(event, union_key)
            if predicate(union_element):
                handler(union_element)
        return event_type, wrapped_handler
    return wrap


def keyup_handler(sdl_key):
    """Executes the wrapped function only if the `sdl_key` is lifted."""
    return event_handler("SDL_KEYUP", "key", lambda key : key.keysym.sym == sdl_key)


def windowevent_handler(windowevent_type):
    """Executes the wrapped function only if it is a window event of type `windowevent_type`."""
    def predicate(window):
        return window.event == windowevent_type

    return event_handler("SDL_WINDOWEVENT", "window", predicate)


class Events:
    # event_handlers :: Map EventId [Callable]
    event_handler_type = Callable[[sdl2.SDL_Event], None]
    event_handlers: Dict[str, List[event_handler_type]] = {}

    @staticmethod
    def handle_events():
        for event in sdl2.ext.get_events():
            listeners = Events.event_handlers.get(event.type, [])
            for listener in listeners:
                listener(event)

    @staticmethod
    def add_listener(event_type: str, listener: Callable[[sdl2.SDL_Event], None]):
        if not listener or not event_type:
            return

        event_id = sdl2.__dict__.get(event_type)
        if type(event_id) is int:
            if event_id not in Events.event_handlers:
                Events.event_handlers[event_id] = []
            Events.event_handlers[event_id].append(listener)
        else:
            raise ValueError(
                f"No event id to the event type {event_type}, see: https://wiki.libsdl.org/SDL_Event"
            )
