from Server.tcp_server import TCPServer


def test():
    server = TCPServer()
    while True:
        server.connect()
        server.receiveFile()
    server.close()


test()
