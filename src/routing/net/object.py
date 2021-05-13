class ConnectPoint:
    def __init__(self, sw, port):
        self.sw = sw
        self.port = port

class Link:
    def __init__(self, src, dst, delay):
        self.src = src
        self.dst = dst
        self.delay = delay

class Switch:
    def __init__(self, id, name, controller_address):
        self.id = id
        self.name = name
        self.controller_address = controller_address

class Host:
    def __init__(self, mac, connectPoint):
        self.mac = mac
        self.connectPoint = connectPoint