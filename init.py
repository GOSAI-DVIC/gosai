import os

from core.console.console import Console
from core.hal.hal import HardwareAbstractionLayer
from core.manager.app_manager import AppManager
from core.server.server import Server, start_chrome

os.environ["LOG_LEVEL"] = "2"

hal = HardwareAbstractionLayer()
server = Server(hal)
server.start()

app_manager = AppManager(hal, server)
app_manager.start("menu")

start_chrome()

console = Console(hal, server, app_manager)
console.start()
