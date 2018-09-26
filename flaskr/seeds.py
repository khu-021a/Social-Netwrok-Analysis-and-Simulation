import snap as sp 
import graph
import centr
import random

def rnd(nodesnum, seedsnum):
    return random.sample(list(range(nodesnum)),seedsnum)

def select_by_centr(centr, seedsnum):
    sortedindicator = sorted(list(enumerate(centr)),key = lambda el: el[1],reverse = True)
    return  [indicator[0] for indicator in sortedindicator[0:seedsnum]]
 
def seeds(net, number, alg):
    total_node_num = net.GetNodes()
    if number >= total_node_num:
        return [node.GetId() for node in net.Nodes()]
    else:
        if alg == "DegreeCentr":
            return select_by_centr(centr.centr(net), number)
        elif alg == "BetweennessCentr":
            return select_by_centr(centr.between(net), number)
        elif alg == "ClosenessCentr":
            return select_by_centr(centr.closeness(net),number)
        elif alg == "EigenVectorCentr":
            return select_by_centr(centr.eigenvector(net),number)
        else:
            return rnd(total_node_num, number)
        
    


g1= graph.sp.GenPrefAttach( 100,3 )

print(seeds(g1, 3, "DegreeCentr"))

# print([node.GetId() for node in g1.Nodes()])



