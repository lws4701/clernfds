from Client.tcp_client import TCPClient
from Client.archive import Archive


def test():
    client = TCPClient()
    client.connect()
    client.sendFile("img1.jpg")
    client.close()

    imgZip = Archive()
    for i in range(1, 6):
        imgZip.add("img%i.jpg" % i)
    imgZip.close()  # Absolutely necessary for the function to send a valid value

    client.connect()
    client.sendFile(imgZip.fileName)
    client.close()

    """client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.close()
    client.connect()
    client.send("Hello Anton.")
    client.close()"""


test()
