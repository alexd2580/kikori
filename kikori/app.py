import ctypes
import logging

import sdl2

from .event import Events, keyup_handler, windowevent_handler

logger = logging.getLogger(__name__)


class Box:
    def __init__(self, rect):
        self.rect = rect

    def render(self):
        App.rect(self.rect, 100, 100, 100, 255)

    def update(self):
        self.rect.x = (self.rect.x + 10) % 4000


class App:
    BORDER_WIDTH_PERCENT = 10
    # 30 FPS.
    FRAME_DURATION = 1000 / 30

    running = False

    num_displays = None
    windows = []
    events = Events()

    # if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
    #     print("DOWN  ", event.button.windowID, event.button.button, event.button.x, event.button.y)
    # if event.type == sdl2.SDL_MOUSEMOTION:
    #     print("MOTION", event.motion.windowID, event.motion.x, event.motion.y, event.motion.xrel, event.motion.yrel)
    # if event.type == sdl2.SDL_MOUSEBUTTONUP:
    #     print("UP    ", event.button.windowID, event.button.button, event.button.x, event.button.y)

    @staticmethod
    @windowevent_handler(sdl2.SDL_WINDOWEVENT_LEAVE)
    def handle_window_leave(window):
        window_id = window.windowID
        [window_rect] = [
            window["internal_rect"] for window in App.windows if window["window_id"] == window_id
        ]

        x = ctypes.c_int()
        y = ctypes.c_int()
        sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        abs_x = window_rect.x + x.value
        x_left = abs_x < window_rect.x + window_rect.w / 2
        offset_x = -3 if x_left else 3
        abs_x = abs_x + offset_x

        abs_y = window_rect.y + y.value
        y_up = abs_y < window_rect.y + window_rect.h / 2
        offset_y = -3 if y_up else 3
        abs_y = abs_y + offset_y

        matching = [
            window
            for window in App.windows
            if App.point_in_rect((abs_x, abs_y), window["internal_rect"])
        ]
        if matching:
            window = matching[0]
            rect = window["internal_rect"]
            sdl2.SDL_WarpMouseInWindow(window["window"], abs_x - rect.x, abs_y - rect.y)

    @staticmethod
    @keyup_handler(sdl2.SDLK_q)
    def handle_q(_):
        logger.info("Pressed q. Exiting now.")
        App.running = False

    @staticmethod
    @windowevent_handler(sdl2.SDL_WINDOWEVENT_CLOSE)
    def handle_window_close(_):
        App.running = False

    @staticmethod
    def prepare():
        App.running = True

        App.num_displays = sdl2.SDL_GetNumVideoDisplays()
        logger.info(f"Number of displays: {App.num_displays}")

        for display in range(0, App.num_displays):
            rect = sdl2.SDL_Rect()
            sdl2.SDL_GetDisplayBounds(display, rect)

            border_width = rect.w * App.BORDER_WIDTH_PERCENT / 100
            border_height = rect.h * App.BORDER_WIDTH_PERCENT / 100
            window = sdl2.SDL_CreateWindow(
                f"{display}".encode("ascii"),
                0,
                0,
                int(rect.w - 2 * border_width),
                int(rect.h - 2 * border_height),
                int(sdl2.SDL_WINDOW_BORDERLESS),
            )
            window_id = sdl2.SDL_GetWindowID(window)

            renderer = sdl2.SDL_CreateRenderer(window, -1, 0)
            sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255)

            sdl2.SDL_ShowWindow(window)
            sdl2.SDL_SetWindowPosition(
                window, int(rect.x + border_width), int(rect.y + border_height)
            )

            scale_factor = (100 - 2 * App.BORDER_WIDTH_PERCENT) / 100
            internal_rect = sdl2.SDL_Rect(
                int(rect.x * scale_factor),
                int(rect.y * scale_factor),
                int(rect.w * scale_factor),
                int(rect.h * scale_factor),
            )

            App.windows.append(
                {
                    "rect": rect,
                    "internal_rect": internal_rect,
                    "window_id": window_id,
                    "window": window,
                    "renderer": renderer,
                }
            )

        Events.add_listener(*App.handle_window_leave)
        Events.add_listener(*App.handle_window_close)
        Events.add_listener(*App.handle_q)

    @staticmethod
    def point_in_rect(point, rect):
        x, y = point
        x_intersects = x >= rect.x and x <= rect.x + rect.w
        y_intersects = y >= rect.y and y <= rect.y + rect.h
        return x_intersects and y_intersects

    @staticmethod
    def rects_intersect(a, b):
        x_intersects = a.x < b.x + b.w and b.x < a.x + a.w
        y_intersects = a.y < b.y + b.h and b.y < a.y + a.h
        return x_intersects and y_intersects

    @staticmethod
    def rect_on(display, rect, r, g, b, a):
        renderer = App.windows[display]["renderer"]
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, a)
        sdl2.SDL_RenderFillRect(renderer, rect)

    @staticmethod
    def rect(rect, r, g, b, a):
        for index, window in enumerate(App.windows):
            display_rect = window["internal_rect"]
            if App.rects_intersect(display_rect, rect):
                local_rect = sdl2.SDL_Rect(
                    rect.x - display_rect.x, rect.y - display_rect.y, rect.w, rect.h
                )
                App.rect_on(index, local_rect, r, g, b, a)

    @staticmethod
    def run():
        boxes = [Box(sdl2.SDL_Rect(0, int(1080 * 0.8 / 2) - 50, 100, 100))]

        last_tick = sdl2.SDL_GetTicks()
        while App.running:
            for box in boxes:
                box.update()

            for window in App.windows:
                renderer = window["renderer"]
                sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255)
                sdl2.SDL_RenderClear(renderer)

            for box in boxes:
                box.render()

            for window in App.windows:
                renderer = window["renderer"]
                sdl2.SDL_RenderPresent(renderer)

            Events.handle_events()
            current_tick = sdl2.SDL_GetTicks()
            last_tick = last_tick + App.FRAME_DURATION
            delay = last_tick - current_tick
            sdl2.SDL_Delay(int(max(0, delay)))
