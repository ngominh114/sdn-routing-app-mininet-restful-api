from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import pandas as pd
import time
import random
import re
import os
from threading import Timer
start_time = time.time()
links = {}
latest_traffic_data = {}
net = Mininet(controller=RemoteController)
node_num = 14
dataset = {
    "timestamp": [],
    "node1": [],
    "node2": [],
    "packets": [],
    "bytes": [],
    "bw": [],
    "delay": []
}
number_of_data = 0
def generate_data():
    global number_of_data
    global dataset
    print("generate")
    for link in net.links:
        intf1 = link.intf1
        intf2 = link.intf2
        node1 = intf1.node
        node2 = intf2.node
        if ('h' in str(node1) or 'h' in str(node2)):
            continue
        number_of_data += 1
        if number_of_data%2 == 0:
            data = create_data(intf1, intf2)
        else: 
            data = create_data(intf2, intf1)
        dataset["timestamp"].append(data["timestamp"])
        dataset["node1"].append(data["node1"])
        dataset["node2"].append(data["node2"])
        dataset["packets"].append(data["packets"])
        dataset["bytes"].append(data["bytes"])
        dataset["bw"].append(data["bw"])
        dataset["delay"].append(data["delay"])
    print(len(dataset["timestamp"]))
    if len(dataset["timestamp"]) > 100:
        df = pd.DataFrame.from_dict(dataset)
        dataset = {
            "timestamp": [],
            "node1": [],
            "node2": [],
            "packets": [],
            "bytes": [],
            "bw": [],
            "delay": []
        }
        df.to_csv('data/%d.csv'%int(time.time()))
        print("create data")
    Timer(1,generate_data).start()
def create_data(intf1, intf2):
    sw_src = str(intf1.node)
    sw_dst = str(intf2.node)
    delay = measure_delay(sw_src, sw_dst)
    packets_rate, bytes_rate, timestamp = get_traffic_rate(intf1, intf2)
    bw = links[sw_src][sw_dst]["bw"]
    data = {
        "timestamp": timestamp,
        "node1": sw_src,
        "node2": sw_dst,
        "packets": packets_rate,
        "bytes": bytes_rate,
        "bw": bw,
        "delay":delay
    }
    return data

def get_traffic_rate(intf1, intf2):
    s1 = intf1.node
    s2 = intf2.node
    traffic = create_traffic(s1, intf1)
    latest_traffic = get_latest_traffic(str(s1), str(s2))
    packets = traffic["packets"] - latest_traffic["packets"]
    transmited_bytes = traffic["bytes"] - latest_traffic["bytes"]
    times = traffic["time"] - latest_traffic["time"]
    packets_rate = packets/times
    bytes_rate = transmited_bytes/times
    latest_traffic_data[str(s1)][str(s2)] = traffic
    latest_traffic_data[str(s2)][str(s1)] = traffic
    return packets_rate, bytes_rate, traffic["time"]

def create_traffic(sw, intf):
    currentTime = time.time()
    result = sw.dpctl("dump-ports", str(intf))
    result = result.split()
    index = result.index("rx")
    packets_str = result[index+1]
    bytes_str = result[index+2]
    packets = int(re.search(r'\d+', packets_str).group())
    transmit_bytes = int(re.search(r'\d+', bytes_str).group())
    traffic = {"packets":packets, "bytes":transmit_bytes, "time":currentTime}
    return traffic

def get_latest_traffic(sw1, sw2):
    if not sw2 in latest_traffic_data[sw1]:
        return {"packets":0, "bytes":0, "time":start_time}
    return latest_traffic_data[sw1][sw2]

def measure_delay(sw1, sw2):
    h_test1 = net.getNodeByName("h_test1")
    h_test2 = net.getNodeByName("h_test2")
    for intf in h_test1.intfList():
        if intf.isUp():
            h_test1.cmd("ifconfig %s down"%str(intf))
    for intf in h_test2.intfList():
        if intf.isUp():
            h_test2.cmd("ifconfig %s down"%str(intf))
    link = links[sw1][sw2]["link"]
    intf1 = link.intf1      #intf s1 to s2
    intf2 = link.intf2      #intf s2 to s1
    s1 = intf1.node
    s2 = intf2.node
    link1 = links[str(s1)]["h_test1"]
    link2 = links[str(s2)]["h_test2"]
    net.configLinkStatus(str(s1), 'h_test1', 'up')
    net.configLinkStatus(str(s2), 'h_test2', 'up')

    h_test1.setIP('10.0.0.200',intf=link1.intf2)
    h_test2.setIP('10.0.0.201',intf=link2.intf2)

    os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(s1, str(link1.intf1), str(link.intf1)))
    os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(s2, str(link.intf2), str(link2.intf1)))

    os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(s1, str(link.intf1), str(link1.intf1)))
    os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(s2, str(link2.intf1), str(link.intf2)))
    
    x = pingAndParseResult(h_test1, h_test2)
    # rs = net.iperf((h_test1,h_test2))
    # print(rs)
    os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(s1, str(link1.intf1)))
    os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(s2, str(link.intf2)))
    os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(s1, str(link.intf1)))
    os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(s2, str(link2.intf1)))
    print(x)
    if len(x) ==0:
        return 100
    return x[1]

def pingAndParseResult(h1, h2):
    rs = h1.cmd("ping -c1", h2.IP())
    rs_split = rs.split()
    x = re.findall("\d+\.\d+", rs_split[-2])
    return x
    
def prepare():
    i=0
    for sw in net.switches:
        i += 1
        if i==1:
            continue
        net.configLinkStatus(str(sw), "h_test1", 'down')
        net.configLinkStatus(str(sw), "h_test2", 'down')

def generate():
    for i in range(1, node_num + 1):
        sw = 's%d' %i
        net.addSwitch(sw)
        links.setdefault(sw, {})
        latest_traffic_data.setdefault(sw, {})

    # Create nodes
    for i in range(1, node_num + 1):
        if i < 10:
            net.addHost('h%d' %i, ip = '10.0.0.%d' %i, mac = '00:00:00:00:01:0%d' %i)
        else:
            net.addHost('h%d' %i, ip = '10.0.0.%d' %i, mac = '00:00:00:00:01:%d' %i)

    print "*** Creating host-switch links"
    for i in range(1, node_num + 1):
        net.addLink('s%d' %i, 'h%d'%i, cls=TCLink, bw=15)

    print "*** Creating switch-switch links"
    link_from = [1,2,2,2,2,2,3,3,5,7,8,8,9,9,10,11,12,13]
    link_to = [2,3,4,5,7,8,4,5,6,9,9,12,10,13,11,13,13,14]
    for lf, lt in zip(link_from, link_to):
        bw = random.uniform(8, 20)
        sw_src = 's%d' % int(lf)
        sw_dst = 's%d' % int(lt)
        link = net.addLink(sw_src, sw_dst, cls=TCLink, bw=bw)
        links.setdefault(sw_src, {})
        links.setdefault(sw_dst, {})
        data = {
            "link": link,
            "bw":bw
        }
        links[sw_src][sw_dst] = data
        links[sw_dst][sw_src] = data
    
    h_test1 = net.addHost("h_test1", ip='10.0.0.200')
    h_test2 = net.addHost("h_test2", ip='10.0.0.201')

    for i in range(node_num):
        sw_name = "s%d"%(i+1)
        link1 = net.addLink(sw_name,"h_test1")
        link2 = net.addLink(sw_name,"h_test2")
        links[sw_name]["h_test1"] = link1
        links[sw_name]["h_test2"] = link2
    # Add Controllers
    c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    time.sleep(5)
    net.start()
def bso():
    global start_time
    # Create switches
    generate()
    prepare()
    #Wait for controller to update paths in network
    time.sleep(5)

    #Run traffic generator script
    CLI(net, script='traffic-gen-script1.sh')
    start_time = time.time()
    currentTime = time.time()
    time.sleep(1)
    generate_data()
    print("RUN TIME: " + str(time.time() - currentTime))
    CLI(net)
    for host in net.hosts:
        print(host)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    bso()
