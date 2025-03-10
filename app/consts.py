# stdlib #
import re
import socket

# pypi #
import rcon


SUPPORTED_PLATFORMS = ["win32", "linux"]

VBCABLE_NAME = "CABLE Input (VB-Audio Virtual Cable)"

SINK_NAME = "tf2gpt_virtual_input"
SOURCE_NAME = "tf2gpt_virtual_microphone"

RE_USERNAME = re.compile(r'.*(?= :)')
RE_MESSAGE = re.compile(r'(?<=. : ).*')

CONNECT_EXCEPTIONS = (
    ConnectionRefusedError,
    ConnectionResetError,
    rcon.SessionTimeout,
    rcon.WrongPassword,
    rcon.EmptyResponse,
    socket.timeout
)

SOURCE_ADDRESS = '127.0.0.1'
SOURCE_PORT = 27015
