import requests
import io
import json

d = requests.get("https://webbtc.com/block/000000000000000001806a922d4d35a37ad9324c690f72d556c6445cb7a9c214.json")

base_url = "https://webbtc.com/block/"
url = base_url + "000000000000000001a1f18b82dcb6696db3136a601c1ac53b59db13201b18b7.json"
d = requests.get("https://webbtc.com/block/000000000000000001a1f18b82dcb6696db3136a601c1ac53b59db13201b18b7.json?raw")
print d
j = d.text
print j
data = json.loads(j)
print data

import copy
chain = []
num_blocks = 0
max_blocks = 10
base_url = "https://webbtc.com/block/"
url = base_url + "000000000000000001a1f18b82dcb6696db3136a601c1ac53b59db13201b18b7.json"
while num_blocks < max_blocks:
    d = requests.get(url)
    j = d.text
    data = json.loads(j)
    reqd = {}
    reqd["hash"] = copy.copy(data["hash"])
    reqd["prev_block"] = copy.copy(data["prev_block"])
    reqd["tx"] = []
    for i in range(0, len(data["tx"])):
        mp = copy.copy(data["tx"][i])
        del mp["ver"]
        del mp["lock_time"]
        del mp["size"]
        del mp["in"]
        del mp["out"]
        mp["in"]=[]
        mp["out"]=[]
        print data
        for j in range(0, len(data["tx"][i]["in"])):
            np={}
            np = copy.copy(data["tx"][i]["in"][j])
            if "scriptSig" in np:
                del np["scriptSig"]
            print np
            mp["in"].append(np)
        for j in range(0, len(data["tx"][i]["out"])):
            np={}
            np = copy.copy(data["tx"][i]["out"][j])
            if "scriptPubKey" in np:
                del np["scriptPubKey"]
            mp["out"].append(np)
        reqd["tx"].append(mp)
    chain.append(reqd)
    num_blocks = num_blocks + 1
    url = base_url + reqd["prev_block"] + ".json"
