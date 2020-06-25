import socket


class TCPServer:
    """
    TCP Server Side of the connection between Server and host
    You need to explicitly call connect to be able to receive data
    Receive does not implicitly close the connection so it can be called over and over
    """

    host = None  # server address eg.) 127.0.0.1 (local)
    port = None  # port number eg.) 1025–65535
    s = socket.socket()  # server socket
    c = None  # client socket
    cAddress = None

    def __init__(self, host: str = socket.gethostname(), port: int = 8080):
        print("Server Connected")
        if 1025 < port < 65535:
            self.port = port
        else:
            self.port = 8080
            print("*** TCP Server - {} is out of bounds and the default port 8080 has been used ***".format(port))

        # no efficient way to check host it just wont work if wrong.
        self.host = host

    def setPort(self, port: int):
        """Set the server port"""
        self.port = port

    def setHost(self, host: str):
        """Set the server address"""
        self.host = host

    def connect(self):
        """Connect client and server"""
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(1)
            self.c, self.cAddress = self.s.accept()
            print("Connection from: {}".format(str(self.cAddress)))
        except Exception as err_type:
            print("\n*** TCP Server \"{}\" error while connecting client to server***\n".format(err_type))

    def receive(self):
        """Send data between Server and host"""
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
                print("\n*** TCP Server \"{}\" client has not been connected  to server***\n")
        except Exception as err_type:
            print("\n*** TCP Server \"{}\" error while trying to send***\n".format(err_type))

    def close(self):
        """ Close connection between the Server and the host"""
        try:
            if self.c is not None:
                self.c.close()
                c = None
                print("Server Disconnected")
            else:
                print("\n*** TCP Server - Already Disconnected ***\n")
        except Exception as err_type:
            print("\n*** TCP Server \"{}\" error while closing connection***\n".format(err_type))

    def data(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
