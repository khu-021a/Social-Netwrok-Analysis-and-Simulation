import json
from osgeo import ogr

def shp2geojson(fp, layer_num=0):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(fp, 0)
    layer = shapefile.GetLayer(layer_num)
    features = [feature.ExportToJson(as_object=True) for feature in layer]
    return json.dumps({'type': 'FeatureCollection', 'features': features})

def getNetwork(fp):
    with open(fp, 'r') as f:
        lines = f.readlines()
        print len(lines)
        line1 = lines[0]
        print line1
        summary = line1.strip().split('#')
        node_num = int(summary[1])
        edge_num = int(summary[3])
        count = 0

        feature_dict = { 
            "type": "FeatureCollection",
            "features": []
        }

        points = {}

        while count < (node_num + edge_num):
            count += 1
            line = lines[count]
            if count <= node_num:
                node_els = line.strip().split('#')
                id = int(node_els[0])
                lon = float(node_els[1])
                lat = float(node_els[2])
                points[id] = [lon, lat]
                feature_dict['features'].insert(0, {
                    "id": id,
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon,lat]
                    }
                })
            else:
                edge_els = line.strip().split(',')
                edge_point1 = int(edge_els[0])
                edge_point2 = int(edge_els[1])
                feature_dict['features'].append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [ points[edge_point1], points[edge_point2] ]
                        }
                    }
                )
        return feature_dict

def getWeightMatrix(fp):
    with open(fp, 'r') as f:
        return [[float(el) for el in line.strip().split('#')] for line in f.readlines()]

if __name__ == '__main__':
    '''
    with open('x.json', 'w') as f:
        j = shp2geojson('../files/JayLee/SocialNetworkSimulator/Shapefile/SRATiger2010.shp')
        f.write(j)
    '''
    x = getNetwork('/Users/jianfengzhu/Desktop/project /input/CityNetwork1.txt')
    y = getWeightMatrix('/Users/jianfengzhu/Desktop/project /input/WeightMatrix326.txt')
    print x
    print y
