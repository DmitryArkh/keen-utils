import json
import re

from json_minify import json_minify
from ssh_manager import SSHManager
from flask import Flask, jsonify, request, send_from_directory
from settings import *

app = Flask(__name__, static_folder='static/assets', static_url_path='/assets')

keenetic_ssh = SSHManager(HOST, SSH_PORT, KEENETIC_USER, KEENETIC_PASSWORD, timeout=60)
entware_ssh = SSHManager(HOST, ENTWARE_SSH_PORT, ENTWARE_USER, ENTWARE_PASSWORD, timeout=60)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        output = keenetic_ssh.execute_command('show system')

        resp = {}
        for match in re.finditer(r'(\w+):\s*([\d/]+|\S+)', output):
            key, value = match.groups()
            resp[key] = value

        if 'memory' in resp:
            memory_used, memory_total = map(int, resp['memory'].split('/'))
            resp['mem'] = str(round((memory_used / memory_total) * 100, 2))

        return jsonify(resp)

    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/api/dns', methods=['GET', 'PUT', 'DELETE'])
def manage_dns():
    try:
        if request.method == 'GET':
            output = keenetic_ssh.execute_command('show dns-proxy')

            records = []
            proxy_configs = output.split('proxy-config:')
            if len(proxy_configs) > 1:
                first_proxy_config = proxy_configs[1].strip()
                records = re.findall(r'static_a\s*=\s*([^\s]+)\s+([^\s]+)', first_proxy_config)

            resp = [
                {'hostname': hostname, 'ip': ip}
                for hostname, ip in records
                if not any(hostname == domain or hostname.endswith(f".{domain}") for domain in STATIC_DNS_EXCLUDED_DOMAINS)
            ]
            return jsonify(resp)

        else:
            domain = request.json.get('domain')
            ip = request.json.get('ip')

            if not domain or not ip:
                return jsonify({'ok': False, 'message': 'Both domain and ip are required'}), 400

            if request.method == 'PUT':
                keenetic_ssh.execute_command(f'ip host {domain} {ip}')
                keenetic_ssh.execute_command('system configuration save')
                return jsonify({'ok': True, 'message': f'Domain {domain} added with IP {ip}'}), 200
            elif request.method == 'DELETE':
                keenetic_ssh.execute_command(f'no ip host {domain} {ip}')
                keenetic_ssh.execute_command('system configuration save')
                return jsonify({'ok': True, 'message': f'Domain {domain} removed with IP {ip}'}), 200

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/xkeen/status', methods=['GET'])
def get_xkeen_status():
    try:
        output = entware_ssh.execute_command('xkeen -status', remote_shell=True)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        status = ansi_escape.sub('', output)

        match status:
            case 'Прокси-клиент запущен':
                return jsonify({'ok': True, 'status': 'running'})
            case 'Прокси-клиент не запущен':
                return jsonify({'ok': True, 'status': 'stopped'})
            case _:
                return jsonify({'ok': True, 'status': 'stopped'})

    except Exception as e:
        return jsonify({'ok': False, 'message': str(e) or 'XKeen not available'}), 500


@app.route('/api/xkeen/<string:action>', methods=['POST'])
def manage_xkeen(action):
    try:
        match action:
            case 'start':
                entware_ssh.execute_command_realtime('xkeen -start', remote_shell=True)
                return jsonify({'ok': True, 'message': 'XKeen started successfully'}), 200
            case 'restart':
                entware_ssh.execute_command_realtime('xkeen -restart', remote_shell=True)
                return jsonify({'ok': True, 'message': 'XKeen restarted successfully'}), 200
            case 'stop':
                entware_ssh.execute_command_realtime('xkeen -stop', remote_shell=True)
                return jsonify({'ok': True, 'message': 'XKeen stopped successfully'}), 200
            case _:
                return jsonify({'ok': False, 'message': 'Unknown action'}), 400

    except Exception as e:
        return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/api/files/<string:file>', methods=['GET', 'PUT'])
def access_entware_file(file):
    if file not in ENTWARE_FILES:
        return jsonify({'ok': False, 'message': 'Unknown file'}), 404

    if request.method == 'GET':
        try:
            content = entware_ssh.read_file(ENTWARE_FILES[file]['path'])
            if ENTWARE_FILES[file]['type'] == 'json':
                try:
                    data = json.loads(json_minify(content))
                    return jsonify(data)
                except Exception:
                    raise Exception('Requested file has invalid JSON syntax')
            return content, 200
        except Exception as e:
            return jsonify({'ok': False, 'message': str(e)}), 500

    elif request.method == 'PUT':
        if ENTWARE_FILES[file]['read_only']:
            return jsonify({'ok': False, 'message': 'File is not writable'}), 403
        try:
            content = request.json.get('content')
            if ENTWARE_FILES[file]['type'] == 'json':
                try:
                    json.loads(content)
                except Exception:
                    raise Exception('Uploaded content has invalid JSON syntax')
            entware_ssh.write_file(ENTWARE_FILES[file]['path'], content)
            return jsonify({'ok': True, 'message': 'File updated successfully'}), 200
        except Exception as e:
            return jsonify({'ok': False, 'message': str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == 'favicon.ico':
        return send_from_directory('static', 'favicon.ico')
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
