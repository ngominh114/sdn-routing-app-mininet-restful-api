import object.TrafficSelector
import object.TrafficTreatment
import object.Flow
def makeFlow(deviceId, inPort, outPort, dst):
    selector = TrafficSelector()
    treatment = TrafficTreatment()
    selector.matchEthDst(dst['mac'])
    selector.matchInPort(inPort)
    treatment.setOutput(outPort)
    flow = Flow(50000, 2, True, deviceId, treatment, selector)
    return flow

def setFlow(net, data, flows):
    for flow in flows:
        
    return

def installFlow(path, data, src, dst):
    flows = []
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
    
    setFlow(flows)

