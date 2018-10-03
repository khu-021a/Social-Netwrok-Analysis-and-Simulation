import graph
import snap 
import random 

def datatransfer(net, seed_list = [], ol_list = []):
    links=[]
    nodes = []
    link_id = 0
    for ni in net.Nodes():
        curr_id = ni.GetId()
        nodes.append({"id": curr_id, 'seed': (curr_id in seed_list), 'opinion_leader': (curr_id in ol_list)})
    #print(nodes)
    
    for EI in net.Edges():
        links.append({"id":link_id,"source":EI.GetSrcNId(),"target":EI.GetDstNId()})
        link_id += 1
    #print(links)
    return {"nodes":nodes, "links":links}




Rnd = snap.TRnd(1,0)
UGraph1 = graph.samllworld_gnm(10, 2, 0, Rnd)
print(datatransfer(UGraph1))