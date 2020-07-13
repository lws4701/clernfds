import socket
from concurrent.futures import ThreadPoolExecutor


class TCPServer:
    """
    TCP Server Side of the connection between Server and host
    Running listenLoop Prepares the server to listen to all possible receive files.
    Run listenLoop on seperate thread.
    """
    host = None  # server address eg.) 127.0.0.1 (local)
    port = None  # port number eg.) 1025–65535
    s = None
    receivedZips = []

    def __init__(self, host: str = socket.gethostname(), port: int = 8080):
        """
        Connects this server object to the host IP and Port
        :param host: //IP
        :param port:
        """
        print("Server Online")
        if 1025 < port < 65535:
            self.port = port
        else:
            self.port = 8080
            print(
                "*** TCP Server - {} is out of bounds and the default port 8080 has been used ***".format(port))
        # no efficient way to check host it just wont work if wrong.
        self.host = host
        self.s = socket.socket()
        self.s.bind((self.host, self.port))

    def listenLoop(self):
        """
        Main Functionality Loop.
        Run in separate thread in the start_server file.
        :return: NULL
        """
        try:
            while True:
                self.s.listen()
                c, c_address = self.s.accept()
                print("Connection from: {}".format(str(c_address)))
                # Receives file while listening to next file.
                ThreadPoolExecutor().submit(self.__receiveFile, c)
        except Exception as err_type:
            print(
                "*** TCP Server \"{}\" error while connecting client to server***".format(err_type))

    def __receiveFile(self, c):
        """
        Receive file from client
        :param c: //Client
        :return: NULL // appends to received that can be dynamically checked
        """
        try:
            if c is not None:
                file_header = c.recv(512).decode().strip()
                response = file_header.upper() + " RECEIVED"
                with open(file_header, "wb") as write_file:
                    while True:
                        bytes_read = c.recv(1024)
                        if not bytes_read:
                            break
                        write_file.write(bytes_read)
                        # print("+", end="")
                        # TCP Response
                        c.send(response.encode('utf-8'))
                    write_file.close()
                print("%s Received" % file_header)
                c.close()
                if file_header != "contacts.txt":
                    self.received.append(file_header)
        except Exception as err_type:
            print(
                "*** TCP SERVER \"%s\" error while trying to receive file ***" % err_type)

    def __str__(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
