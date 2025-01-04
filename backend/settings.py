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
