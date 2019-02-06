"""Main."""
__version__ = "0.1.0"

import logging

import sdl2
import sdl2.ext

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


class Box:
    pass


class App:
    BORDER_WIDTH = 50
    # 30 FPS.
    FRAME_DURATION = 1000 / 30

    def __init__(self):
        self.running = True
        self.num_displays = None
        self.windows = []
        self.renderers = []

    def handle_events(self):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_WINDOWEVENT:
                if event.window.event == sdl2.SDL_WINDOWEVENT_CLOSE:
                    self.running = False
                    break

    def prepare(self):
        self.num_displays = sdl2.SDL_GetNumVideoDisplays()
        logger.info(f"Number of displays: {self.num_displays}")

        for display in range(0, self.num_displays):
            rect = sdl2.SDL_Rect()
            sdl2.SDL_GetDisplayBounds(display, rect)
            window = sdl2.SDL_CreateWindow(
                f"{display}".encode('ascii'),
                0, 0,
                rect.w - 2 * self.BORDER_WIDTH,
                rect.h - 2 * self.BORDER_WIDTH,
                int(sdl2.SDL_WINDOW_BORDERLESS)
            )

            renderer = sdl2.SDL_CreateRenderer(window, -1, 0)
            sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255)

            sdl2.SDL_ShowWindow(window)
            sdl2.SDL_SetWindowPosition(
                window, rect.x + self.BORDER_WIDTH, rect.y + self.BORDER_WIDTH
            )

            self.windows.append(window)
            self.renderers.append(renderer)

    def run(self):
        last_tick = sdl2.SDL_GetTicks()
        while self.running:
            for renderer in self.renderers:
                sdl2.SDL_RenderClear(renderer)
                sdl2.SDL_RenderPresent(renderer)

            self.handle_events()
            current_tick = sdl2.SDL_GetTicks()
            last_tick = last_tick + self.FRAME_DURATION
            delay = last_tick - current_tick
            print(delay)
            sdl2.SDL_Delay(int(max(0, delay)))


def main():
    logger.info("Initializing")
    sdl2.ext.init()

    app = App()
    app.prepare()
    app.run()

    sdl2.ext.quit()
    logger.info("Terminated")
