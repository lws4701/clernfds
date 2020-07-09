from time import sleep

from Server.tcp_server import TCPServer
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def test():
    server = TCPServer()
    # Put the receive loop into a separate thread so that you can actually do stuff while listening.
    ThreadPoolExecutor().submit(server.listenLoop)
    while True:
        sleep(5)
        # You can dynamically check which files have been received.
        print(server.received)


test()
