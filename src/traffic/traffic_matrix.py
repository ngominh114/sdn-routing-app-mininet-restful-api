import os
import re
import time

class TrafficMatrixManager():
    def __init__(self):
        self.current_traffic_matrix = {}
        self.latest_traffic_matrix = {}
        self.current_time = 0
        self.latest_time = 0
    
    def measure_traffic_metrix(self, net):
        matrix = {}
        netLinks = net.links
        for netLink in netLinks:
            intf1 = netLink.intf1
            intf2 = netLink.intf2
            node1 = intf1.node
            node2 = intf2.node
            if (("h" in str(node1)) or (("h" in str(node2)))):
                continue
            result1 = node1.dpctl("dump-ports", str(intf1))
            result2 = node2.dpctl("dump-ports", str(intf2))

            result1 = result1.split()
            result2 = result2.split()

            index1 = result1.index("rx")
            index2 = result2.index("rx")

            packets_str1 = result1[index1+1]
            bytes_str1 = result1[index1+2]
            packets_str2 = result2[index2+1]
            bytes_str2 = result2[index2+2]

            packets1 = int(re.search(r'\d+', packets_str1).group())
            transmit_bytes1 = int(re.search(r'\d+', bytes_str1).group())
            packets2 = int(re.search(r'\d+', packets_str2).group())
            transmit_bytes2 = int(re.search(r'\d+', bytes_str2).group())
            traffic1 = {"packet":packets1, "bytes":transmit_bytes1}
            traffic2 = {"packet":packets2, "bytes":transmit_bytes2}

            node1_str = str(node1)
            node2_str = str(node2)
            if not node1_str in matrix:
                matrix[node1_str] = {}
            matrix[node1_str][node2_str] = traffic1

            if not node2_str in matrix:
                matrix[node2_str] = {}
            matrix[node2_str][node1_str] = traffic2
        self.latest_traffic_matrix = self.current_traffic_matrix
        self.current_traffic_matrix = matrix
        self.latest_time = self.current_time
        self.current_time = time.time()*1000
    
    
        
                
            