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

    def execute_command(self, command, remote_shell=False, ignore_errors=False):
        with self.lock:
            self._ensure_connection()

            if remote_shell:
                command = 'sh -l -c "%s"' % command
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if ('error' in output.lower() or 'ошибка' in output.lower() or error) and not ignore_errors:
                raise Exception(output)

            self.last_access_time = time.time()
            return output

    def execute_command_realtime(self, command, remote_shell=False, stop_keyword=None, error_keyword='failed'):
        with self.lock:
            self._ensure_connection()
            transport = self.client.get_transport()
            channel = transport.open_session()
            if remote_shell:
                command = 'sh -l -c "%s"' % command
            channel.exec_command(command)

            full_output = []
            while True:
                if channel.recv_ready():
                    output = channel.recv(1024).decode('utf-8')
                    full_output.append(output)

                    if stop_keyword and stop_keyword in output.lower():
                        channel.close()
                        break

                    if error_keyword and error_keyword in output.lower():
                        raise Exception(output)

                if channel.exit_status_ready():
                    break

            self.last_access_time = time.time()
            return ''.join(full_output)

    def read_file(self, remote_path):
        command = f'cat {remote_path}'
        return self.execute_command(command, ignore_errors=True)

    def write_file(self, remote_path, content):
        command = f'echo \'{content.replace('\'', '\\\'')}\' > {remote_path}'
        self.execute_command(command)

    def delete_file(self, remote_path):
        command = f'rm -f {remote_path}'
        self.execute_command(command)

    def close(self):
        with self.lock:
            self._disconnect()
