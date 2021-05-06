import json
from collections import namedtuple
from json import JSONEncoder
class DataAPI:
    def __init__(self):
        self.data = {}
    def read(self, data_dir = "data/data.json"):
        with open(data_dir, 'r') as data_file:
            objs = json.loads(data_file.read())
            self.data = objs
            data_file.close()
    def save(self, data_dir = "data/data.json"):
        jsonString = json.dumps(self.data, default=lambda o: o.__dict__, indent=4)
        with open(data_dir, 'w') as outfile:
            outfile.write(jsonString)
            outfile.close()
    def addHost(self, host):
        self.data['hosts'].append(host)
        self.save()
    def updateDevice(self, devices):
        self.data['devices'] = devices
        self.save()
    def addLink(self, link):
        self.data['links'].append(link)
        self.save()
    def delHost(self, mac):
        hosts = self.data['hosts']
        for i, host in enumerate(hosts):
            if host['mac'] == mac:
                hosts.pop(i)
                self.save()
                break
    def delDevice(self, id):
        devices = self.data['devices']
        for i, device in enumerate(devices):
            if device['id'] == id:
                devices.pop(i)
                self.save()
                break

    def delLink(self, srcId, dstId):
        links = self.data['links']
        for i, link in enumerate(links):
            if link['src']['deviceId'] == srcId and link['dst']['deviceId'] == dstId:
                links.pop(i)
                self.save()
                break
def read():
    with open("data/data.json", 'r') as data_file:
        objs = json.loads(data_file.read())
        data_file.close()
        return objs




