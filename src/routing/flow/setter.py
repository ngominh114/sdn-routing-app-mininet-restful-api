from object import Flow
import os
import time
def makeFlow(switch, inPort, outPort,src, dst):
    flow = Flow(switch, inPort, outPort,src['mac'], dst['mac'])
    return flow

def setFlow(net, flows):
    for flow in flows:
        sw_str = flow.switch
        sw = net.getNodeByName(sw_str)
        # sw.dpctl("add-flow", "in_port=%s,dl_src=%s,dl_dst=%s,priority=50000,actions=output:%s" %(flow.in_port, flow.dl_src, flow.dl_dst, flow.out_port))
        os.system("ovs-ofctl add-flow %s in_port=%s,dl_src=%s,dl_dst=%s,priority=50000,actions=output:%s" %(sw_str, flow.in_port, flow.dl_src, flow.dl_dst, flow.out_port))
def installFlow(net, path, src, dst):
    flows = []
    if (len(path) == 0):
        flow = makeFlow(src['connectPoint']['sw'], 
                        src['connectPoint']['port'], 
                        dst['connectPoint']['port'],
                        src,
                        dst)
        flows.append(flow)
    else:
        srcFlow = makeFlow(src['connectPoint']['sw'], 
                            src['connectPoint']['port'], 
                            path[0]['src']['port'],
                            src,
                            dst)
        flows.append(srcFlow)

        dstFlow = makeFlow(dst['connectPoint']['sw'], 
                            path[-1]['dst']['port'], 
                            dst['connectPoint']['port'], 
                            src,
                            dst)
        flows.append(dstFlow)
        for i in range(1, len(path)):
            inPort = path[i-1]['dst']['port']
            outPort = path[i]['src']['port']
            switch = path[i]['src']['sw']
            flow = makeFlow(switch, inPort, outPort, src, dst)
            flows.append(flow)
    setFlow(net, flows)