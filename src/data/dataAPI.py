import json
from collections import namedtuple
from json import JSONEncoder
from routing.net.object import Switch
from routing.net.object import Host
from routing.net.object import Link
from routing.net.object import ConnectPoint
import os
def objToDict(obj):
    jsonStr = json.dumps(obj, default=lambda o: o.__dict__, indent=4)
    return json.loads(jsonStr)
class DataAPI:
    def __init__(self):
        self.component_data_dir ="data/component"
        self.data = {}
        self.data["switches"] = []
        self.data["links"] = []
        self.data["hosts"] = []
    def updateData(self):
        list_file = os.listdir(self.component_data_dir)
        hosts = []
        switches = []
        links = []
        for file_name in list_file:
            with open(self.component_data_dir + "/" + file_name, 'r') as data_file:
                objs = json.loads(data_file.read())
                if ("hosts" in objs):
                    hosts = hosts + objs["hosts"]
                if ("switches" in objs):
                    switches = switches + objs["switches"]
                if ("links" in objs):
                    links = links + objs["links"]
                data_file.close()
        self.data["hosts"] = hosts
        self.data["switches"] = switches
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
    def updateSwitch(self, data):
        controller_ip = data["ctrl_ip"]
        file_dir = "data/component/" + controller_ip+".json"
        objs = {}
        with open(file_dir, "r") as data_file:
            objs = json.loads(data_file.read())
            switches = data["switches"]
            objs["switches"] = switches
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
    def delSwitch(self, id):
        switches = self.data['switches']
        for i, switch in enumerate(switches):
            if switch['id'] == id:
                switches.pop(i)
                self.save()
                break

    def delLink(self, srcId, dstId):
        links = self.data['links']
        for i, link in enumerate(links):
            if link['src']['switchId'] == srcId and link['dst']['switchId'] == dstId:
                links.pop(i)
                self.save()
                break
    def getHostByMac(self, mac):
        for host in self.data["hosts"]:
            if host["mac"] == mac:
                return host
    
    def buildHostDataByNet(self, net):
        hosts = []
        netHosts = net.hosts
        for netHost in netHosts:
            intf = netHost.intfList()[0]
            link = intf.link
            if("s" in str(link.intf1.node)):
                sw = str(link.intf1.node)
                port = str(link.intf1.name)
            else:
                sw = str(link.intf2.node)
                port = str(link.intf2.name)
            connectPoint = ConnectPoint(sw, port)
            host = Host(netHost.MAC(), connectPoint)
            hosts.append(objToDict(host))
        self.data["hosts"] = hosts
        self.save()
        

    def buildLinkDataByNet(self, net):
        links = []
        netLinks = net.links
        for netLink in netLinks:
            intf1 = netLink.intf1
            intf2 = netLink.intf2
            node1 = str(intf1.node)
            node2 = str(intf2.node)
            if (("h" in str(node1)) or ("h" in str(node2))):
                continue
            src = ConnectPoint(node1, str(intf1.name))
            dst = ConnectPoint(node2, str(intf2.name))
            links.append(objToDict(Link(src, dst, 1.0)))
            links.append(objToDict(Link(dst, src, 1.0)))
        self.data["links"] = links
        self.save()
    
    def buildSwitchDataByNet(self, net, ctrl_ip = "192.168.1.1"):
        switches = []
        netSwitches = net.switches
        for netSwitch in netSwitches:
            switch = Switch(str(netSwitch.dpid), str(netSwitch), ctrl_ip)
            switches.append(objToDict(switch))
        self.data["switches"] = switches
        self.save()


    def updateDataByNet(self, net):
        self.buildHostDataByNet(net)
        self.buildLinkDataByNet(net)
        self.buildSwitchDataByNet(net)

    def getLink(self, src, dst):
        for link in self.data["links"]:
            if(link["src"]["sw"] == src and link["dst"]["sw"]==dst):
                return link

