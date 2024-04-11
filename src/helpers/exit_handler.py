import signal
from src.helpers.fexit import fexit

def signal_handler(sig, frame):
    fexit('Ctrl+C handled. exit.')

signal.signal(signal.SIGINT, signal_handler)
