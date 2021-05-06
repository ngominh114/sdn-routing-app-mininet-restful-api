class ConnectPoint:
    def __init__(self, deviceId: str, port: str):
        self.deviceId = deviceId
        self.port = port

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
        self.mac = mac
        self.connectPoint = connectPoint