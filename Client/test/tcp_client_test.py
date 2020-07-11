from time import sleep

from Client.tcp_client import TCPClient
from Client.archive import Archive
from concurrent.futures import ThreadPoolExecutor


def test():

    # client.connect()
    # client.sendFile("img1.jpg")
    # client.close()

    img_zip = Archive()
    for i in range(1, 6):
        img_zip.add("img%i.jpg" % i)
    img_zip.close()  # Absolutely necessary for the function to send a valid value
    client = TCPClient()
    client2 = TCPClient()
    client3 = TCPClient()
    # client.sendFile(img_zip.file_name)
    # client2.sendFile("img1.jpg")
    # client3.sendFile("img2.jpg")
    ThreadPoolExecutor().submit(client.sendFile, img_zip.file_name)
    ThreadPoolExecutor().submit(client2.sendFile, "img1.jpg")
    ThreadPoolExecutor().submit(client3.sendFile, "img3.jpg")

    """client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.send("Hello Anton.")
    client.close()
    client.connect()
    client.send("Hello Anton.")
    client.close()"""


test()
