import networkx
import random
import os
from mininet.net import Mininet
from mininet.node import RemoteController
import random
import configparser
from data.dataAPI import DataAPI
from flask import Flask
from flask import request
from routing.flow import setter
from routing.path.pathCreate import PathCreator
import json


api = DataAPI()
api.read()
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read('config.ini')
number_of_controllers = len(config["CONTROLLER_IP"])
c_ip = []
for i in range(number_of_controllers):
    c_ip.append(config["CONTROLLER_IP"]["ip_%s"%i])
filename = config["DIRECTORIES"]["topo"]
graph = networkx.read_graphml(filename)
sw_dict = {}
net = Mininet(topo=None, build=False)
nodes = graph.nodes()
edges = graph.edges()
dpid_prefix = "00000000000000"
hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]
number_of_switch = 0
for node in nodes:
    if node in hosts:
        net.addHost(node)
    else:
        number_of_switch = number_of_switch + 1
        dpid = dpid_prefix + "%02d"%number_of_switch
        sw = net.addSwitch(node, dpid = dpid)
        sw_dict[dpid] = sw
if len(hosts) == 0:
    for node in nodes:
        net.addHost("h%s" % node)
        net.addLink("h%s" % node, node)
for edge in edges:
    linkopts = dict()
    net.addLink(edge[0], edge[1], **linkopts)

pathCreate = PathCreator()

def findPathAndSetFlow(src, dst):
    srcHost = api.getHostByMac(src)
    dstHost = api.getHostByMac(dst)
    path = pathCreate.createPath(srcHost["connectPoint"]["deviceId"], dstHost["connectPoint"]["deviceId"])
    setter.installFlow(sw_dict, path, srcHost, dstHost)
app = Flask(__name__)
@app.route('/pingAll', methods = ['GET'])
def pingAll():
    n1 = net.getNodeByName('n1')
    n2 = net.getNodeByName('n2')
    net.ping([n1, n2])
    return ""
@app.route('/cancel', methods=['GET'])
def cancel():
    os.system("")
@app.route('/', methods=['GET'])
def start():
    controllers = []
    for i in range(number_of_controllers):
        controller = net.addController("c%s"%i, controller=RemoteController, ip=c_ip[i])
        controllers.append(controller)
    net.build()
    for i, sw in enumerate(net.switches):
        c = random.choice(controllers)
        sw.start([c])
    net.waitConnected()
    return ""
@app.route('/setFlow', methods = ["POST"])
def setFlow():
    data = request.get_json()
    src = data["src"]
    dst = data["dst"]
    findPathAndSetFlow(src, dst)
    return ""
@app.route('/shutdown', methods = ['GET'])
def bye():
    net.stop()
    os.system("sudo mn -c")
    return ""

@app.route('/devices.store', methods = ['POST'])
def updateDevices():
    data = request.get_json()
    api.updateDevice(data)
    pathCreate.graph.updateGraph(api.data)
    return ""


@app.route('/hosts.store', methods = ['POST'])
def updateHosts():
    data = request.get_json()
    api.updateHost(data)
    return ""
@app.route("/add-flow", methods=["GET"])
def add_flow():
    os.system("sudo ovs-ofctl add-flow n0 in_port=3,actions=output:2")
    os.system("sudo ovs-ofctl add-flow n0 in_port=2,actions=output:3")
    return ""

@app.route("/testPing", methods=["GET"])
def test_ping():
    
    return ""

@app.route('/links.store', methods = ['POST'])
def updateLinks():
    data = request.get_json()
    api.updateLink(data)
    pathCreate.graph.updateGraph(api.data)
    return ""
