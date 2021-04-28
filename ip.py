import sys,os
from pythonping import executor as exe
from pythonping import payload_provider
from netaddr import *

class IPs (object):
    ips = {}
    range_top = 0
    range_bottom = 0
    timeout_ips = 0

    def __init__(self):
        ips = {}

    def add_ip(self, raw_ip, ip_name=''):
        try:
            ip_network = IPNetwork(raw_ip)
        except:
            ip_network = [IP.ZERO_IP]

        for ip_n in ip_network:
            sip_n = str(ip_n)
            self.ips[sip_n] = IP(sip_n, ip_name)
        
        return self.ips[sip_n]

    def add_ips(self, raw_ips, raw_ips_names):
        for i, raw_ip in enumerate(raw_ips):
            self.add_ip(raw_ip, raw_ips_names[i])
        return self.ips
    
    def get_ip(self, ip):
        return self.ips[ip]
    
    def get_ips(self):
        return self.ips
    
    def get_ips_range(self, top, bottom, is_drawing_timeout=True):
        range_ips = []
        self.range_top = top
        self.range_bottom = bottom
        self.timeout_ips = 0
        for idx, ip in enumerate(self.ips):
            if (idx > top) and (idx < bottom):
                if is_drawing_timeout:
                    range_ips.append(ip)
                else:
                    if not self.ips[ip].is_timeout:
                        range_ips.append(ip)
                    else:
                        self.timeout_ips += 1 
        return range_ips
    
    def get_range(self):
        return (self.range_top, self.range_bottom)
    
    def del_ip(self, ip):
        del self.ips[ip]

class IP (object):
    # Config
    ip = ''
    log_history = False
    name = ''

    # Ping activity data 
    is_timeout = False
    ping_last = 0
    ping_history = []
    provider = {}
    com = {}

    # Constants
    PAYLOAD = 'test'
    TIMEOUT = 2
    MS_DECIMALS = 2
    ZERO_IP = '0.0.0.0'

    def __init__(self, ip, name=''):
        self.ip = ip
        self.init_provider()
        self.name = name

    def init_provider(self):
        try:
            self._init_provider()
        except:
            self.ip = self.ZERO_IP
            self._init_provider()
    
    def _init_provider(self):
        self.provider = payload_provider.Repeat(self.PAYLOAD, 1)
        self.com = exe.Communicator(self.ip, self.provider, self.TIMEOUT)
    
    def edit_ip(self, ip):
        self.ip = ip
        self.init_provider()
    
    def ping(self):
        # Execute ping
        self.com.run(match_payloads=False)

        # Convert to ms rounded to 2 decimal places
        self.ping_last = round(self.com.responses._responses[0].time_elapsed * 1000, self.MS_DECIMALS)
        self.is_timeout = self.ping_last == (self.TIMEOUT * 1000)

        if self.log_history:
            self.ping_history.append(self.com.responses._responses[0])
        
    def toggle_log_history(self, log_history='none'):
        if log_history == 'none':
            self.log_history = not self.log_history
        else:
            self.log_history = log_history

    def clear_history(self):
        self.ping_history = []

    def get_result(self):
        return (self.ip, self.name, self.ping_last, self.is_timeout)

    # Custom name
    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    # Timeout
    def set_timeout(self, timeout):
        self.TIMEOUT = timeout