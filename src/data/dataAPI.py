import json
from collections import namedtuple
from json import JSONEncoder
import os
class DataAPI:
    def __init__(self):
        self.component_data_dir ="data/component"
        self.data = {}
        self.data["devices"] = []
        self.data["links"] = []
        self.data["hosts"] = []
    def updateData(self):
        list_file = os.listdir(self.component_data_dir)
        hosts = []
        devices = []
        links = []
        for file_name in list_file:
            with open(self.component_data_dir + "/" + file_name, 'r') as data_file:
                objs = json.loads(data_file.read())
                if ("hosts" in objs):
                    hosts = hosts + objs["hosts"]
                if ("devices" in objs):
                    devices = devices + objs["devices"]
                if ("links" in objs):
                    links = links + objs["links"]
                data_file.close()
        self.data["hosts"] = hosts
        self.data["devices"] = devices
        self.data["links"] = links
        self.save()
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
    def updateHost(self, data):
        controller_ip = data["ctrl_ip"]
        file_dir = "data/component/" + controller_ip+".json"
        objs = {}
        with open(file_dir, "r") as data_file:
            objs = json.loads(data_file.read())
            hosts = data["hosts"]
            objs["hosts"] = hosts
            data_file.close()
        with open(file_dir,'w') as data_file:
            jsonString = json.dumps(objs, default=lambda o: o.__dict__, indent=4)
            data_file.write(jsonString)
            data_file.close()
        self.updateData()
    def updateDevice(self, data):
        controller_ip = data["ctrl_ip"]
        file_dir = "data/component/" + controller_ip+".json"
        objs = {}
        with open(file_dir, "r") as data_file:
            objs = json.loads(data_file.read())
            devices = data["devices"]
            objs["devices"] = devices
            data_file.close()
        with open(file_dir,'w') as data_file:
            jsonString = json.dumps(objs, default=lambda o: o.__dict__, indent=4)
            data_file.write(jsonString)
            data_file.close()
        self.updateData()
    def updateLink(self, data):
        controller_ip = data["ctrl_ip"]
        file_dir = "data/component/" + controller_ip+".json"
        objs = {}
        with open(file_dir, "r") as data_file:
            objs = json.loads(data_file.read())
            links = data["links"]
            objs["links"] = links
            data_file.close()
        with open(file_dir,'w') as data_file:
            jsonString = json.dumps(objs, default=lambda o: o.__dict__, indent=4)
            data_file.write(jsonString)
            data_file.close()
        self.updateData()
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
    def getHostByMac(self, mac):
        for host in self.data["hosts"]:
            if host["mac"] == mac:
                return host




