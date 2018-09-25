import snap as sp

# IsDir = False 

def rnd_gnm(*args, **kwargs):
    return sp.GenRndGnm(*args, **kwargs)

def prefattach_gnm(*args, **kwargs):
    return sp.GenPrefAttach(*args, **kwargs)

def samllworld_gnm(*args, **kwargs):
    return sp.GenSmallWorld(*args, **kwargs)

#print(rnd_gnm(sp.PUNGraph,20,30))