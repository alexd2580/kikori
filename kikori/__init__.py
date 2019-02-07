"""Main."""
__version__ = "0.1.0"

import logging

import sdl2
import sdl2.ext

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


class Box:
    def __init__(self, rect):
        self.rect = rect

    def render(self, graphics):
        graphics.rect(self.rect, 100, 100, 100, 255)


class Graphics:
    BORDER_WIDTH_PERCENT = 10
    # 30 FPS.
    FRAME_DURATION = 1000 / 30

    def __init__(self):
        self.running = True
        self.num_displays = None
        self.windows = []

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

            border_width = rect.w * self.BORDER_WIDTH_PERCENT / 100
            border_height = rect.h * self.BORDER_WIDTH_PERCENT / 100
            window = sdl2.SDL_CreateWindow(
                f"{display}".encode('ascii'),
                0, 0,
                int(rect.w - 2 * border_width),
                int(rect.h - 2 * border_height),
                int(sdl2.SDL_WINDOW_BORDERLESS)
            )

            renderer = sdl2.SDL_CreateRenderer(window, -1, 0)
            sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255)

            sdl2.SDL_ShowWindow(window)
            sdl2.SDL_SetWindowPosition(
                window,
                int(rect.x + border_width),
                int(rect.y + border_height),
            )

            scale_factor = (100 - 2 * self.BORDER_WIDTH_PERCENT) / 100
            internal_rect = sdl2.SDL_Rect(
                int(rect.x * scale_factor), int(rect.y * scale_factor),
                int(rect.w * scale_factor), int(rect.h * scale_factor)
            )
            print(rect, internal_rect)

            self.windows.append((rect, internal_rect, window, renderer))

    @staticmethod
    def rects_intersect(a, b):
        x_intersects = a.x < b.x + b.w and b.x < a.x + a.w
        y_intersects = a.y < b.y + b.h and b.y < a.y + a.h
        return x_intersects and y_intersects

    def rect_on(self, display, rect, r, g, b, a):
        _, _, _, renderer = self.windows[display]
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, a)
        sdl2.SDL_RenderFillRect(renderer, rect)

    def rect(self, rect, r, g, b, a):
        for index, (_, display_rect, _, _) in enumerate(self.windows):
            if Graphics.rects_intersect(display_rect, rect):
                local_rect = sdl2.SDL_Rect(
                    rect.x - display_rect.x, rect.y - display_rect.y,
                    rect.w, rect.h
                )
                self.rect_on(index, local_rect, r, g, b, a)

    def run(self):
        boxes = [Box(sdl2.SDL_Rect(0, 500, 100, 100))]

        last_tick = sdl2.SDL_GetTicks()
        while self.running:
            for box in boxes:
                box.rect.x = (box.rect.x + 10) % 4000
                print(box.rect.x)
                # box.rect.y = box.rect.y + 10 % 1080

                # intersects = any([
                #     Graphics.rects_intersect(box.rect, internal_rect)
                #     for _, internal_rect, _, _ in self.windows
                # ])
                # if not intersects:
                #     box.rect.y = 0

            for _, _, _, renderer in self.windows:
                sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255)
                sdl2.SDL_RenderClear(renderer)

            for box in boxes:
                box.render(self)

            for _, _, _, renderer in self.windows:
                sdl2.SDL_RenderPresent(renderer)

            self.handle_events()
            current_tick = sdl2.SDL_GetTicks()
            last_tick = last_tick + self.FRAME_DURATION
            delay = last_tick - current_tick
            sdl2.SDL_Delay(int(max(0, delay)))


def main():
    logger.info("Initializing")
    sdl2.ext.init()

    graphics = Graphics()
    graphics.prepare()
    graphics.run()

    sdl2.ext.quit()
    logger.info("Terminated")
