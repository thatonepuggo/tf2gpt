# pypi #
from rcon.source import Client

# local #
from .config import config
from .conlog import ConLog

client: Client = None

conlog: ConLog = ConLog(config.data["logfile"])

is_connected: bool = False
previously_connected: bool = False
first_connection: bool = True
