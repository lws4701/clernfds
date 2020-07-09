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
    received = []

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
                c, cAddress = self.s.accept()
                print("Connection from: {}".format(str(cAddress)))
                ThreadPoolExecutor().submit(self.receiveFile, c)  # Receives file while listening to next file.
        except Exception as err_type:
            print(
                "*** TCP Server \"{}\" error while connecting client to server***".format(err_type))

    def receiveFile(self, c):
        """
        Receive file from client
        :param c: //Client
        :return: NULL // appends to received that can be dynamically checked
        """
        try:
            if c is not None:
                fileHeader = c.recv(512).decode().strip()
                response = fileHeader.upper() + " RECEIVED"
                with open(fileHeader, "wb") as writeFile:
                    while True:
                        bytesRead = c.recv(1024)
                        if not bytesRead:
                            break
                        writeFile.write(bytesRead)
                        #print("+", end="")
                        # TCP Response
                        c.send(response.encode('utf-8'))
                    writeFile.close()
                print("%s Received" % fileHeader)
                c.close()
                self.received.append(fileHeader)
        except Exception as err_type:
            print(
                "*** TCP SERVER \"%s\" error while trying to receive file ***" % err_type)

    # Antiquated..
    def receiveTEST(self, c):
        """
        ***ANTIQUATED***
        Receive data between and host
        """
        try:
            if c is not None:
                while True:
                    data = c.recv(1024).decode('utf-8')
                    if not data:
                        break
                    print('From online user: ' + data)
                    data = data.upper()
                    c.send(data.encode('utf-8'))
                    c.close()
            else:
                print(
                    "*** TCP Server \"{}\" client has not been connected  to server***")
        except Exception as err_type:
            print(
                "*** TCP Server \"{}\" error while trying to send***".format(err_type))

    def data(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
