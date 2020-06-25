from Server.tcp_server import TCPServer


def test():
    server = TCPServer()
    while True:
        server.connect()
        server.receive()
    server.close()


test()
