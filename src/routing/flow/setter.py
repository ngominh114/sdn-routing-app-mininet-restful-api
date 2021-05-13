from object import Flow
import os
def makeFlow(switch, inPort, outPort, dst):
    flow = Flow(switch, inPort, outPort, dst['mac'], 2)
    return flow

def setFlow(switchDict, flows):
    for flow in flows:
        sw = flow.switch
        os.system("sudo ovs-ofctl add-flow %s in_port=%s,dl_dst=%s,priority=50000,actions=output:%s" %(sw, flow.in_port, flow.dl_dst, flow.out_port))
def installFlow(switchDict, path, src, dst):
    flows = []
    if (len(path) == 0):
        flow = makeFlow(src['connectPoint']['sw'], 
                        src['connectPoint']['port'], 
                        dst['connectPoint']['port'], dst)
        flows.append(flow)
    else:
        srcFlow = makeFlow(src['connectPoint']['sw'], 
                            src['connectPoint']['port'], 
                            path[0]['src']['port'], dst)
        flows.append(srcFlow)

        dstFlow = makeFlow(dst['connectPoint']['sw'], 
                            path[-1]['dst']['port'], 
                            dst['connectPoint']['port'], 
                            dst)
        flows.append(dstFlow)

        for i in range(1, len(path)):
            inPort = path[i-1]['dst']['port']
            outPort = path[i]['src']['port']
            switchId = path[i]['src']['sw']
            flow = makeFlow(switchId, inPort, outPort, dst)
    
    setFlow(switchDict, flows)

