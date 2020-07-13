import socket
import os


class TCPClient:
    """
    TCP Client Side of the connection between client and host
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

    def __connect(self):
        """
        Helper Function to the sendFile function that connects to the server
        :return:
        """
        try:
            self.s = socket.socket()
            self.s.connect((self.host, self.port))
            print("Client Connected")
        except Exception as err_type:
            print(
                f"*** TCP Client \"{err_type}\" error while connecting to server***")

    def sendFile(self, file_name):
        """Send file from client to server"""
        self.__connect()
        try:
            if self.s is not None:
                if file_name is None:
                    print("No file selected to send")
                else:
                    fileSize = os.path.getsize(file_name)
                    # Send header with file_name and size
                    header = os.path.basename(file_name).ljust(512)
                    self.s.sendall(header.encode('utf-8'))
                    # Send file as bytestring
                    with open(file_name, "rb") as sendingFile:
                        sent = 0
                        response = None
                        while sent < fileSize:
                            bytes_read = sendingFile.read(1024)
                            self.s.sendall(bytes_read)
                            sent += 1024
                            #print("+", end="")
                            # TCP Response
                            response = self.s.recv(1024).decode('utf-8')
                    sendingFile.close()
                    print("Server Response = %s" % response)
                    # os.remove(file_name)
        except Exception as err_type:
            print("***TCP Client \"%s\" error while trying to send ***" % err_type)
        self.__close()

    def __close(self):

        """
        Helper Function to Sendfile function that closes the connection
        :return:
        """
        try:
            if self.s is not None:
                self.s.close()
                self.s = None
                print("Client Disconnected")
            else:
                print("*** TCP Client - Already Disconnected ***\n")
        except Exception as err_type:
            print(
                "*** TCP Client \"{}\" error while closing connection***".format(err_type))

    def __str__(self):
        print("Host is: {} and the port is {}".format(self.host, self.port))
