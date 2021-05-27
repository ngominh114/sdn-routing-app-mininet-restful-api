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
    "backward_pkts_rate": [],
    "forward_pkts_rate": [],
    "backward_bytes_rate": [],
    "forward_bytes_rate":[],
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
        dataset["backward_pkts_rate"].append(data["backward_pkts_rate"])
        dataset["forward_pkts_rate"].append(data["forward_pkts_rate"])
        dataset["backward_bytes_rate"].append(data["backward_bytes_rate"])
        dataset["forward_bytes_rate"].append(data["forward_bytes_rate"])
        dataset["bw"].append(data["bw"])
        dataset["delay"].append(data["delay"])
    print(len(dataset["timestamp"]))
    if len(dataset["timestamp"]) > 300:
        df = pd.DataFrame.from_dict(dataset)
        dataset = {
            "timestamp": [],
            "node1": [],
            "node2": [],
            "backward_pkts_rate": [],
            "forward_pkts_rate": [],
            "backward_bytes_rate": [],
            "forward_bytes_rate":[],
            "bw": [],
            "delay": []
        }
        df.to_csv('data/%d.csv'%int(time.time()))
        print("create data")
    Timer(1,generate_data).start()
def create_data(intf1, intf2):
    s1 = str(intf1.node)
    s2 = str(intf2.node)
    delay = measure_delay(s1, s2)
    traffic_rate, timestamp = get_traffic_rate(intf1)
    bw = links[s1][s2]["bw"]
    data = {
        "timestamp": timestamp,
        "node1": s1,
        "node2": s2,
        "backward_pkts_rate": traffic_rate["rx_pkts_rate"],
        "forward_pkts_rate": traffic_rate["tx_pkts_rate"],
        "backward_bytes_rate": traffic_rate["rx_bytes_rate"],
        "forward_bytes_rate": traffic_rate["tx_bytes_rate"],
        "bw": bw,
        "delay":delay
    }
    return data

def get_traffic_rate(intf):
    sw = intf.node
    traffic_rate = calc_traffic_rate(sw, intf)
    return traffic_rate, time.time()

def calc_traffic_rate(sw, intf):
    traffic = create_traffic(sw, intf)
    latest_traffic = get_latest_traffic(str(sw), str(intf))
    rx_pkts = traffic["rx_pkts"] - latest_traffic["rx_pkts"]
    tx_pkts = traffic["tx_pkts"] - latest_traffic["tx_pkts"]
    rx_bytes = traffic["rx_bytes"] - latest_traffic["rx_bytes"]
    tx_bytes = traffic["tx_bytes"] - latest_traffic["tx_bytes"]
    times = traffic["time"] - latest_traffic["time"]

    latest_traffic_data[str(sw)][str(intf)] = traffic
    rx_pkts_rate = rx_pkts/times
    tx_pkts_rate = tx_pkts/times
    rx_bytes_rate = rx_bytes/times
    tx_bytes_rate = tx_bytes/times

    return {
        "rx_pkts_rate":rx_pkts_rate,
        "tx_pkts_rate":tx_pkts_rate,
        "rx_bytes_rate":rx_bytes_rate,
        "tx_bytes_rate":tx_bytes_rate
    }

def create_traffic(sw, intf):
    currentTime = time.time()
    result = sw.dpctl("dump-ports", str(intf))
    result = result.split()
    rx_index = result.index("rx")
    rx_pkts_str = result[rx_index+1]
    rx_bytes_str = result[rx_index+2]
    rx_pkts = int(re.search(r'\d+', rx_pkts_str).group())
    rx_transmit_bytes = int(re.search(r'\d+', rx_bytes_str).group())
    tx_index = result.index("tx")
    tx_pkts_str = result[tx_index+1]
    tx_bytes_str = result[tx_index+2]
    tx_pkts = int(re.search(r'\d+', tx_pkts_str).group())
    tx_transmit_bytes = int(re.search(r'\d+', tx_bytes_str).group())
    traffic = {"rx_pkts":rx_pkts, "rx_bytes":rx_transmit_bytes, "tx_pkts":tx_pkts, "tx_bytes": tx_transmit_bytes, "time":currentTime}
    return traffic

def get_latest_traffic(sw, intf):
    if not intf in latest_traffic_data[sw]:
        return {"rx_pkts":0, "rx_bytes":0, "tx_pkts":0, "tx_bytes":0, "time":start_time}
    return latest_traffic_data[sw][intf]

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
        bw = random.uniform(10, 20)
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
    time.sleep(1)
    generate_data()
    CLI(net)
    for host in net.hosts:
        print(host)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    bso()
