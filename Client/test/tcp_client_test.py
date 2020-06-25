from Client.tcp_client import TCPClient


def test():
    client = TCPClient()
    client.connect()
    client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.close()
    client.connect()
    client.send("Hello Anton.")
    client.close()


test()
