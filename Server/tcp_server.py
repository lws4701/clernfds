import socket
import os
import archive


class TCPServer:
    """
    TCP Server Side of the connection between Server and host
    You need to explicitly call connect to be able to receive data
    Receive does not implicitly close the connection so it can be called over and over
    """

    host = None  # server address eg.) 127.0.0.1 (local)
    port = None  # port number eg.) 1025–65535
    c = None  # client socket
    cAddress = None  # client address

    def __init__(self, host: str = socket.gethostname(), port: int = 8080):
        print("Server Online")
        if 1025 < port < 65535:
            self.port = port
        else:
            self.port = 8080
            print(
                "*** TCP Server - {} is out of bounds and the default port 8080 has been used ***".format(port))
        # no efficient way to check host it just wont work if wrong.
        self.host = host

    def connect(self):
        """Connect client and host"""
        try:
            s = socket.socket()
            s.bind((self.host, self.port))
            s.listen()
            self.c, self.cAddress = s.accept()
            print("Connection from: {}".format(str(self.cAddress)))
        except Exception as err_type:
            print(
                "\n*** TCP Server \"{}\" error while connecting client to server***\n".format(err_type))

    def receive(self):
        """Receive data between and host"""
        try:
            if self.c is not None:
                while True:
                    data = self.c.recv(1024).decode('utf-8')
                    if not data:
                        break
                    print('From online user: ' + data)
                    data = data.upper()
                    self.c.send(data.encode('utf-8'))
            else:
                print(
                    "\n*** TCP Server \"{}\" client has not been connected  to server***\n")
        except Exception as err_type:
            print(
                "\n*** TCP Server \"{}\" error while trying to send***\n".format(err_type))

    def receiveFile(self):
        '''Receive file from client'''
        try:
            if self.c is not None:
                fileHeader = self.c.recv().decode('utf-8')
                with open("archives/" + fileHeader, "wb") as writeFile:
                    bytesRead = self.c.recv()
                    writeFile.write(bytesRead)
                    writeFile.close()
                    # zipFile = archive.Archive(fileHeader) TODO: Possibly add extraction to method
                    # zipFile.extract()

        except Exception as err_type:
            print(
                "\n*** TCP SERVER \"%s\" error while trying to receive file ***" % err_type)

    def close(self):
        """ Close connection between the Server and the host"""
        try:
            if self.c is not None:
                self.c.close()
                c = None
                print("Server Offline")
            else:
                print("\n*** TCP Server - Already Disconnected ***\n")
        except Exception as err_type:
            print(
                "\n*** TCP Server \"{}\" error while closing connection***\n".format(err_type))

    def data(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
