from __future__ import print_function
import json
from json import JSONEncoder
try:
    from types import SimpleNamespace as Namespace
except ImportError:
    # Python 2.x fallback
    from argparse import Namespace
class ConnectPoint:
    def __init__(self, deviceId: str, port: str):
        self.deviceId = deviceId, self.port = port

class Link:
    def __init__(self, src: ConnectPoint, dst: ConnectPoint, delay: float):
        self.src = src
        self.dst = dst
        self.delay = delay

class Device:
    def __init__(self, id: str, controller_address: str):
        self.id = id
        self.controller_address = controller_address

class Host:
    def __init__(self, mac: str, connectPoint: ConnectPoint):
        self.mac = mac, self.connectPoint = connectPoint


class Flow:
    def __init__(self, priority, timeout, isPermanent, deviceId, treatment, selector):
        self.priority, self.timeout, self.isPermanent, self.deviceId, self.treatment, self. selector

device1 = Device(1, "192.168.1.1")
device2 = Device(2, "192.168.1.1")
link = Link(device1, device2, 0.1)
def toJson(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, indent=4)
print(toJson(link))
