import re
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/dns', methods=['GET', 'PUT', 'DELETE'])
def manage_dns():
    try:
        if request.method == 'GET':
            output = keenetic_ssh.execute_command('show dns-proxy')

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


@app.route('/api/files/<path:remote_path>', methods=['GET'])
def read_entware_file(remote_path):
    try:
        content = entware_ssh.read_file('/opt/' + remote_path)
        return content, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == 'favicon.ico':
        return send_from_directory('static', 'favicon.ico')
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
