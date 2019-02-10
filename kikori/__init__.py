"""Main."""
__version__ = "0.1.0"

import logging

import sdl2.ext

from .app import App

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initializing")
    sdl2.ext.init()

    App.prepare()
    App.run()

    sdl2.ext.quit()
    logger.info("Terminated")
