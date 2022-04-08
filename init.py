import os

from core.console.console import Console
from core.hal.hal import HardwareAbstractionLayer
from core.logs.logger import Logger
from core.manager.app_manager import AppManager
from core.server.server import Server, start_chrome

os.environ["LOG_LEVEL"] = "2"

server = Server()
server.start()

hal = HardwareAbstractionLayer(server)

logger = Logger(server)
logger.log_listenner()

app_manager = AppManager(hal, server)
app_manager.start("menu")
app_manager.start("show_hands")

start_chrome(server.path)

console = Console(hal, server, app_manager)
console.start()
