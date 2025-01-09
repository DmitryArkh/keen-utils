import time
import paramiko
from threading import Lock

class SSHManager:
    def __init__(self, host, port, username, password, timeout=300):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None
        self.last_access_time = None
        self.lock = Lock()

    def _connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, self.port, self.username, self.password)
        self.last_access_time = time.time()

    def _disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def _ensure_connection(self):
        now = time.time()
        if self.client is None or not self._is_connection_alive() or (self.last_access_time and now - self.last_access_time > self.timeout):
            self._disconnect()
            self._connect()

    def _is_connection_alive(self):
        transport = self.client.get_transport() if self.client else None
        return transport and transport.is_active()

    def execute_command(self, command):
        with self.lock:
            self._ensure_connection()

            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if 'error' in output.lower() or error:
                raise Exception(output)

            self.last_access_time = time.time()
            return output

    def read_file(self, remote_path):
        command = f'cat {remote_path}'
        return self.execute_command(command)

    def write_file(self, remote_path, content):
        command = f'echo \'{content.replace('\'', '\\\'')}\' > {remote_path}'
        self.execute_command(command)

    def delete_file(self, remote_path):
        command = f'rm -f {remote_path}'
        self.execute_command(command)

    def close(self):
        with self.lock:
            self._disconnect()
