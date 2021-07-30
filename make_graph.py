import os
import json

data = [file for file in os.listdir("data") if not file.startswith(".")]
party_data = []

for file in data:
    with open("data/" + file, "r") as fin:
        json_string = fin.readline()
        party_data += json.loads(json_string)

party_data = [party for party in party_data if len(party["colors"]) > 0]
nodes = [{"id":party["id"], "name":party["name"], "ideology":party["ideology"], "color":party["colors"][0]} for party in party_data]
links = []

for partyA in nodes:
    for partyB in [party for party in nodes if party["id"] != partyA["id"]]:
        shared_ideologies = set.intersection(set(partyA["ideology"]), set(partyB["ideology"]))
        if len(shared_ideologies) > 0:
            link = {"source":partyA["id"], "target":partyB["id"], "value":len(shared_ideologies)}
            links.append(link)

print("nodes", len(nodes))
print("links", len(links))

graph = {"nodes":nodes, "links":links}

with open("graph.json", "w") as fout:
    json.dump(graph, fout)
