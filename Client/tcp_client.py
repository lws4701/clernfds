import socket
import os


class TCPClient:
    """
    TCP Client Side of the connection between client and host
    There needs to be an explicit connection call to be able to send to host
    """

    host = None  # server address eg.) 127.0.0.1 (local)
    port = None  # port number eg.) 1025–65535
    s = None  # socket

    def __init__(self, host: str = socket.gethostname(), port: int = 8080):
        if 1025 < port < 65535:
            self.port = port
        else:
            self.port = 8080
            print(
                "*** TCP Client - {} is out of bounds and the default port 8080 has been used ***".format(port))
        # no efficient way to check host it just wont work if wrong.
        self.host = host

    def connect(self):
        """Connect Client to Host Server"""
        try:
            self.s = socket.socket()
            self.s.connect((self.host, self.port))
            print("Client Connected")
        except Exception as err_type:
            print(
                "\n*** TCP Client \"{}\" error while connecting to server***".format(err_type))

    def send(self, data=None):
        """Send data between client and host"""
        try:
            if self.s is not None:
                # dummy data for testing purposes
                if data is None:
                    message = input('What ya wanna send? -> ')
                else:
                    message = data
                while message != '':
                    self.s.send(message.encode('utf-8'))
                    data = self.s.recv(1024).decode('utf-8')
                    print("Server Response = {}".format(data))
                    message = input(
                        "Send another message or just press enter ==> ")
            else:
                print("*** TCP Client - Connection between server has not been made ***")
        except Exception as err_type:
            print(
                "\n*** TCP Client \"{}\" error while trying to send***".format(err_type))

    def sendFile(self, fileName):
        '''Send file from client to server'''
        try:
            if self.s is not None:
                if fileName is None:
                    print("No file selected to send")
                else:
                    fileSize = os.path.getsize(fileName)
                    # Send header with filename and size
                    self.s.send((("File: %s\nSize%s") %
                                 (fileName, fileSize)).encode("utf-8"))
                    # Send file as bytestring
                    with open(fileName, "rb") as sendingFile:
                        self.s.sendall(sendingFile.read())
        except Exception as err_type:
            print("\n***TCP Client \"%s\" error while trying to send ***" % err_type)

    def close(self):
        """ Close connection between the client and the host"""
        try:
            if self.s is not None:
                self.s.close()
                s = None
                print("Client Disconnected")
            else:
                print("\n*** TCP Client - Already Disconnected ***\n")
        except Exception as err_type:
            print(
                "\n*** TCP Client \"{}\" error while closing connection***".format(err_type))

    def data(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
