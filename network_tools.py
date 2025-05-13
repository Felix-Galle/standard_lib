import socket
import threading
import time
import logging
import ssl
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseNetworkTools:
    def __init__(self, port):
        self.port = port
        self.logger = logging.getLogger(self.__class__.__name__)


class LANNetworkTools(BaseNetworkTools):
    def __init__(self, port):
        super().__init__(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def get_ip_address(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.logger.info(f"Local IP Address: {ip_address}")
        return ip_address

    def broadcast_data(self):
        hostname = socket.gethostname()
        ip_address = self.get_ip_address()
        message = f"{hostname},{ip_address}"

        while True:
            self.sock.sendto(message.encode(), ('<broadcast>', self.port))
            self.logger.info(f"Broadcasting: {message}")
            time.sleep(5)

    def receive_broadcast(self):
        self.sock.bind(('', self.port))
        self.logger.info(f"Listening for broadcasts on port {self.port}...")

        while True:
            data, addr = self.sock.recvfrom(1024)
            self.logger.info(f"Received message: {data.decode()} from {addr}")

    def start(self):
        threading.Thread(target=self.broadcast_data).start()
        threading.Thread(target=self.receive_broadcast).start()


class InternetNetworkTools(BaseNetworkTools):
    def __init__(self, port, use_ssl=False):
        super().__init__(port)
        self.use_ssl = use_ssl

    def start_server(self, host='0.0.0.0'):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, self.port))
        server_socket.listen(5)
        self.logger.info(f"Internet server started on {host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            self.logger.info(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        if self.use_ssl:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile='server.crt', keyfile='server.key')
            client_socket = context.wrap_socket(client_socket, server_side=True)
        
        data = client_socket.recv(1024)
        self.logger.info(f"Received: {data.decode()}")
        client_socket.sendall(b"ACK")
        client_socket.close()

    def send_message(self, target_ip, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=target_ip)

        sock.connect((target_ip, self.port))
        sock.sendall(message.encode())
        response = sock.recv(1024)
        self.logger.info(f"Received response: {response.decode()}")
        sock.close()
