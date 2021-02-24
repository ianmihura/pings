import sys,os
from pythonping import executor as exe
from pythonping import payload_provider
from netaddr import *
import pprint

class IPs (object):
    ips = {}

    def __init__(self):
        ips = {}

    def add_ip(self, ip):
        self.ips[ip] = IP(ip)
        return self.ips[ip]

    def add_ips(self, raw_ips):
        ip_list = []
        for raw_ip in raw_ips:
            ip_network = IPNetwork(raw_ip)
            for ip_n in ip_network:
                self.add_ip(str(ip_n))
    
    def get_ip(self, ip):
        return self.ips[ip]
    
    def get_ips(self):
        return self.ips
    
    def del_ip(self, ip):
        del self.ips[ip]

class IP (object):
    ip = ''
    payload = 'test'
    
    # Config constants
    timeout = 1
    log_history = False

    # Ping activity information 
    is_timeout = False
    ping_last = 0
    ping_history = []
    provider = {}
    com = {}

    def __init__(self, ip, timeout=2, payload='test', log_history=False):
        self.ip = ip
        self.timeout = timeout
        self.payload = payload
        self.log_history = log_history

        self.init_provider()

    def init_provider(self):
        try:
            self._init_provider()
        except:
            self.ip = '0.0.0.0'
            self._init_provider()
    
    def _init_provider(self):
        self.provider = payload_provider.Repeat(self.payload, 1)
        self.com = exe.Communicator(self.ip, self.provider, self.timeout)
    
    def edit_ip(self, ip):
        self.ip = ip
        self.init_provider()
    
    def ping(self):
        # Execute ping
        self.com.run(match_payloads=False)

        # Convert to ms rounded to 2 decimal places
        self.ping_last = round(self.com.responses._responses[0].time_elapsed * 1000, 2)
        self.is_timeout = self.ping_last == (self.timeout * 1000)

        if self.log_history:
            self.ping_history.append(self.com.responses._responses[0])
        
    def clear_history(self):
        self.ping_history = []

    def get_result(self):
        return (self.com.socket.destination, self.ping_last, self.is_timeout)
