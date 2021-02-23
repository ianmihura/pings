import sys,os
from pythonping import executor as exe
from pythonping import payload_provider
import i18n

class IPs (object):
    ips = {}

    def __init__(self):
        ips = {}

    def add_ips(self, ips):
        for ip in ips:
            self.add_ip(ip)

    def add_ip(self, ip):
        self.ips[ip] = IP(ip)
        return self.ips[ip]

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
            self.provider = payload_provider.Repeat(self.payload, 1)
            self.com = exe.Communicator(self.ip, self.provider, self.timeout)
        except:
            self.ip = '0.0.0.0'
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
        
        # print(self.get_result())
        
    def clear_history(self):
        self.ping_history = []

    def get_result(self):
        if self.ping_last == 0:
            return i18n.PING_WAITING.format(self.com.socket.destination)
        if self.is_timeout:
            return i18n.PING_TIMEOUT.format(self.com.socket.destination)
        else:
            return i18n.PING_RESULT.format(self.com.socket.destination, self.ping_last)
    