'''
Created on 26.08.2018

@author: rpickhardt
'''
from lightning.lightning import LightningRpc
import json
import time
import pickle

class Autopilot():
    rpc_interface = None
    def __init__(self):
        #FIXME: find out where the config file is placed:
        self.rpc_interface = LightningRpc("/Users/rpickhardt/.lightning/lightning-rpc")

    def __initialize_node_dict(self):
        #FIXME: it is a real problem that we don't know how many nodes there could be
        try:
            node_dict = {}
            nodes = []

            while len(nodes) == 0: 
                peers = self.rpc_interface.listpeers()["peers"]
                if len(peers) < 1:
                    #FIXME: do we have seed nodes?
                    self.rpc_interface.connect("024a8228d764091fce2ed67e1a7404f83e38ea3c7cb42030a2789e73cf3b341365")
                    time.sleep(2)
                nodes = self.rpc_interface.listnodes()["nodes"]

            for node in nodes:
                node_dict[node["nodeid"]] = node
            return node_dict
        except ValueError:
            pass
        return {}
    
    def __initialize_edges_dict(self, node_dict):
        if len(node_dict)==0:
            return {}
        channels = self.rpc_interface.listchannels()["channels"]
        edge_dict = {}
        for channel in channels:
            for key in channel.keys():
                print(key, channel[key])
            break
        
        for channel in channels:
            edge_dict[channel["short_channel_id"]] = channel
            
            for key in ["source", "destination"]:
                if "channels" in node_dict[channel[key]]:
                    node_dict[channel[key]]["channels"].append(channel["short_channel_id"])
                else:
                    node_dict[channel[key]]["channels"]=[channel["short_channel_id"]]
        
        for node_id, metadata in node_dict.items():
            if "channels" in metadata:
                metadata["channels"] = list(set(metadata["channels"]))
                node_dict[node_id] = metadata
                print(node_id, len(metadata["channels"]))  
            
        return node_dict, edge_dict
        
    def run(self):
        #move to constructor and store values as self
        node_dict = {}
        edge_dict = {}
        try:
            #FIXME: problem if the files exist but are not in pickle format
            with open("data/nodes","rb") as in_file:
                node_dict = pickle.load(in_file)
            with open("data/edges","rb") as in_file:
                edge_dict = pickle.load(in_file) 
        except IOError:
            pass
        
        if len(node_dict)==0:
            node_dict = self.__initialize_node_dict()
            node_dict, edge_dict = self.__initialize_edges_dict(node_dict)
        
            with open("data/nodes","wb") as out:
                pickle.dump(node_dict,out,pickle.HIGHEST_PROTOCOL)
            with open("data/edges","wb") as out:
                pickle.dump(edge_dict,out,pickle.HIGHEST_PROTOCOL)
        
        
        print(len(node_dict))
        
if __name__ == '__main__':
    autopilot = Autopilot()
    autopilot.run()
    pass