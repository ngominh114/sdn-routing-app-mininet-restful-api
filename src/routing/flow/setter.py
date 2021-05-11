from object import Flow
import os
def makeFlow(deviceId, inPort, outPort, dst):
    flow = Flow(deviceId, inPort, outPort, dst['mac'], 2)
    return flow

def setFlow(switchDict, flows):
    for flow in flows:
        deviceId = flow.deviceId
        deviceId = deviceId[3:]
        sw = switchDict[deviceId]
        print(sw)
        os.system("sudo ovs-ofctl add-flow n0 in_port=2,actions=output:3")
        os.system("sudo ovs-ofctl add-flow n0 in_port=3,actions=output:2")
        print(os.system("sudo ovs-ofctl dump-flows %s"%sw))
def installFlow(switchDict, path, src, dst):
    flows = []
    if (len(path) == 0):
        flow = makeFlow(src['connectPoint']['deviceId'], 
                        src['connectPoint']['port'], 
                        dst['connectPoint']['port'], dst)
        flows.append(flow)
    else:
        srcFlow = makeFlow(src['connectPoint']['deviceId'], 
                            src['connectPoint']['port'], 
                            path[0]['src']['port'], dst)
        flows.append(srcFlow)

        dstFlow = makeFlow(dst['connectPoint']['deviceId'], 
                            path[-1]['dst']['port'], 
                            dst['connectPoint']['port'], 
                            dst)
        flows.append(dstFlow)

        for i in range(1, len(path)):
            inPort = path[i-1]['dst']['port']
            outPort = path[i]['src']['port']
            deviceId = path[i]['src']['deviceId']
            flow = makeFlow(deviceId, inPort, outPort, dst)
    
    setFlow(switchDict, flows)

