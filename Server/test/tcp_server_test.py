from Server.tcp_server import TCPServer


def test():
    server = TCPServer()
    server.connect()
    while True:
        server.receive()
    server.close()

test()