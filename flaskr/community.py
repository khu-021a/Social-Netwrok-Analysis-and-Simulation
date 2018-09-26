import snap as sp 
import graph
import seeds

def communityCNM(Graph):
    CmtyV = sp.TCnComV()
    sp.CommunityCNM(Graph, CmtyV)
    return [list(cmyt) for cmyt in CmtyV]
    

def find_opinionleaders(communities,proportion):
    index = [seeds.rnd(len(i),int(len(i)*proportion)) for i in communities]
    count = 0
    ids = []
    for count in range(len(communities)):
        c = communities[count]
        i = index[count]
        if len(i) > 0:
            leader = [c[n] for n in i]
            ids.append(leader)
    return [y for x in ids for y in x]

g1= graph.sp.GenPrefAttach( 10,3 )
print(find_opinionleaders(communityCNM(g1), 0.5))


           

    
            



