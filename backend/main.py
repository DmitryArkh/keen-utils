import re
import paramiko
import time
from threading import Lock
from flask import Flask, jsonify, request, send_from_directory
from settings import *

app = Flask(__name__, static_folder='static/assets', static_url_path='/assets')

ssh_client = None
last_access_time = None
lock = Lock()
SSH_TIMEOUT = 60


def is_ssh_alive(client):
    transport = client.get_transport()
    return transport and transport.is_active()


def get_ssh_client():
    global ssh_client, last_access_time

    with lock:
        now = time.time()

        if ssh_client is None or not is_ssh_alive(ssh_client) or (last_access_time and now - last_access_time > SSH_TIMEOUT):
            if ssh_client:
                ssh_client.close()

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(HOST, SSH_PORT, KEENETIC_USER, KEENETIC_PASSWORD)

        last_access_time = now
        return ssh_client


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        client = get_ssh_client()
        stdin, stdout, stderr = client.exec_command('show system')
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            raise Exception(error)

        resp = {}
        for match in re.finditer(r'(\w+):\s*([\d/]+|\S+)', output):
            key, value = match.groups()
            resp[key] = value

        if 'memory' in resp:
            memory_used, memory_total = map(int, resp['memory'].split('/'))
            resp['mem'] = str(round((memory_used / memory_total) * 100, 2))

        return jsonify(resp)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dns', methods=['GET', 'PUT', 'DELETE'])
def manage_dns():
    try:
        client = get_ssh_client()

        if request.method == 'GET':
            stdin, stdout, stderr = client.exec_command('show dns-proxy')
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if 'error' in output.lower():
                raise Exception(output)
            if error:
                raise Exception(error)

            static_a_records = []
            static_aaaa_records = []

            proxy_configs = output.split('proxy-config:')
            if len(proxy_configs) > 1:
                first_proxy_config = proxy_configs[1].strip()

                static_a_records = re.findall(r'static_a\s*=\s*([^\s]+)\s+([^\s]+)', first_proxy_config)
                static_aaaa_records = re.findall(r'static_aaaa\s*=\s*([^\s]+)\s+([^\s]+)', first_proxy_config)

            resp = {
                'static_a': [{'hostname': hostname, 'ip': ip} for hostname, ip in static_a_records],
                'static_aaaa': [{'hostname': hostname, 'ip': ip} for hostname, ip in static_aaaa_records]
            }

            return jsonify(resp)

        elif request.method == 'PUT':
            domain = request.json.get('domain')
            ip = request.json.get('ip')

            if not domain or not ip:
                return jsonify({'ok': False, 'message': 'Both domain and ip are required'}), 400

            command = f'ip host {domain} {ip}'
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if 'error' in output.lower():
                raise Exception(output)
            if error:
                raise Exception(error)

            client.exec_command('system configuration save')
            return jsonify({'ok': True, 'message': f'Domain {domain} added with IP {ip}'}), 200

        elif request.method == 'DELETE':
            domain = request.json.get('domain')
            ip = request.json.get('ip')

            if not domain or not ip:
                return jsonify({'ok': False, 'message': 'Both domain and ip are required'}), 400

            command = f'no ip host {domain} {ip}'
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if 'error' in output.lower():
                if 'no such record' in output.lower():
                    return jsonify({'ok': False, 'message': f'Domain {domain} not found with IP {ip}'}), 404
                raise Exception(output)
            if error:
                raise Exception(error)

            client.exec_command('system configuration save')
            return jsonify({'ok': True, 'message': f'Domain {domain} removed with IP {ip}'}), 200

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == 'favicon.ico':
        return send_from_directory('static', 'favicon.ico')
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
