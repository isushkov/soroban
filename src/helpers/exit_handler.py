import signal

def signal_handler(sig, frame):
    exit('Ctrl+C handled. exit.')

signal.signal(signal.SIGINT, signal_handler)
