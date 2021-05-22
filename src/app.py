import os
import random
import configparser
from data.dataAPI import DataAPI
from net.mininetSim import MininetSim
from flask import Flask
from flask import request
from routing.flow import setter
from routing.path.pathCreate import PathCreator
from traffic.traffic_matrix import TrafficMatrixManager
from mininet.cli import CLI
import json
import time
from threading import Timer
#Read Data
api = DataAPI()
api.read()

#Read config
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read('config.ini')

#Create mininet simulator
mininetSim = MininetSim()
mininetSim.generate(config)
pathCreate = PathCreator()
trafficMatrixManager = TrafficMatrixManager()
def findPathAndSetFlow(src, dst):
    srcHost = api.getHostByMac(str.lower(str(src)))
    dstHost = api.getHostByMac(str.lower(str(dst)))
    if (srcHost == None or dstHost == None):
        return
    currentTime = time.time() * 1000
    path = pathCreate.createPath(srcHost["connectPoint"]["sw"], dstHost["connectPoint"]["sw"])
    findPathTime = time.time()*1000
    setter.installFlow(mininetSim.net, path, srcHost, dstHost)
    setFlowTime = time.time() * 1000
    print("FIND PATH TIME " + str(findPathTime - currentTime))
    print("SET FLOW TIME" + str(setFlowTime - findPathTime))
app = Flask(__name__)
@app.route('/pingAll', methods = ['GET'])
def pingAll():
    mininetSim.pingAll()
    return ""

@app.route("/test", methods=["GET"])
def testtttttttt():
    h_test1 = mininetSim.net.addHost("h_test1")
    h_test2 = mininetSim.net.addHost("h_test2")
    s1 = mininetSim.net.getNodeByName("s1")
    s2 = mininetSim.net.getNodeByName("s2")
    mininetSim.net.addLink(h_test1, s1)
    mininetSim.net.addLink(h_test2, s2)
    h_test1.cmd("ping -c1 " + str(h_test2.IP()))
    return ""

@app.route('/', methods=['GET'])
def start():
    mininetSim.start()
    return ""
@app.route('/setFlow', methods = ["POST"])
def setFlow():
    data = request.get_json()
    src = data["src"]
    dst = data["dst"]
    findPathAndSetFlow(src, dst)
    return ""

@app.route('/data.update', methods = ['GET'])
def updateData():
    api.updateDataByNet(mininetSim.net)
    pathCreate.graph.updateGraph(api.data)
    return ""

@app.route('/connect/<dpid>')
def connect(dpid):
    dpid = mininetSim.dpid_prefix + "%02d"%int(dpid)
    api.updateDataByNet(mininetSim.net)
    pathCreate.graph.updateGraph(api.data)
    if dpid in mininetSim.dpid_to_sw:
        sw = mininetSim.dpid_to_sw[dpid]
        currentTime = time.time()*1000
        sw.dpctl("add-flow", "priority=0,arp,actions=CONTROLLER:65535")
        sw.dpctl("add-flow", "priority=0,dl_type=0x88cc,actions=CONTROLLER:65535")
        sw.dpctl("add-flow", "priority=0,dl_type=0x8942,actions=CONTROLLER:65535")
    return ""

@app.route('/cmd')
def cli():
    CLI(mininetSim.net, script="traffic-gen-script1.sh")
    return ""