import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST', '192.168.1.1')
SSH_PORT = os.getenv('SSH_PORT', 22)
KEENETIC_USER = os.getenv('KEENETIC_USER', 'admin')
KEENETIC_PASSWORD = os.getenv('KEENETIC_PASSWORD')
ENTWARE_SSH_PORT = os.getenv('ENTWARE_SSH_PORT', 222)
ENTWARE_USER = os.getenv('ENTWARE_USER', 'root')
ENTWARE_PASSWORD = os.getenv('ENTWARE_PASSWORD', 'keenetic')

ENTWARE_FILES = {
    'xray-log': {
        'path': '/opt/etc/xray/configs/01_log.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-transport': {
        'path': '/opt/etc/xray/configs/02_transport.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-inbounds': {
        'path': '/opt/etc/xray/configs/03_inbounds.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-outbounds': {
        'path': '/opt/etc/xray/configs/04_outbounds.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-routing': {
        'path': '/opt/etc/xray/configs/05_routing.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-policy': {
        'path': '/opt/etc/xray/configs/06_policy.json',
        'type': 'json',
        'read_only': False,
    },
    'xray-access-log': {
        'path': '/opt/var/log/xray/access.log',
        'type': 'plain',
        'read_only': False,
    },
    'xray-error-log': {
        'path': '/opt/var/log/xray/error.log',
        'type': 'plain',
        'read_only': False,
    },
}

STATIC_DNS_EXCLUDED_DOMAINS = [
    'keenetic.net',
    'keenetic.link',
    'keenetic.pro',
    'keenetic.name',
    'keenetic.io'
]
