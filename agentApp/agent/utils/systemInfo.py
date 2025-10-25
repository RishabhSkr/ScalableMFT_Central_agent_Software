# agent/utils/system_info.py
import socket
import platform
import uuid
import psutil
from typing import Dict

def get_system_info() -> Dict:
    """Collect system information"""
    return {
        'hostname': socket.gethostname(),
        'ip_address': get_local_ip(),
        'mac_address': get_mac_address(),
        'os_info': f"{platform.system()} {platform.release()}",
        'agent_version': '1.0.0',
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }

def get_local_ip() -> str:
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def get_mac_address() -> str:
    """Get MAC address"""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                    for elements in range(0, 2*6, 2)][::-1])
    return mac
