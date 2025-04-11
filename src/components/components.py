#import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class location():
    def __init__(self, postcode :str , coords: tuple):
        self.postcode = postcode
        self.coords = coords


    def __str__(self):
        return f'Postcode {self.postcode} with coords {str(self.coords)}'
    def distanceto(self, otherlocation):
        return distance(self, otherlocation)

#Right so to actually have the distance data, we'll need to pay for google api services. This is unfortuntae. 
#For now we shall use coordinates to calculate the distance between two points (and will assume that we have coords) 

#So we want to define a function that will take two locations and return the distance between them.
#We're not yet competent enought to do this with roads, so shall use diststance as the crow flies.
def distance(loc1, loc2):
    coord1 ,coord2   = loc1.coords, loc2.coords
    #Now, we can use the haversine distance to calulate this distance. I suppose we will need the longitude and latitude of the two points quite accurately.
    #We'll need the Earth's redius in m (which I've done in Manchester as is different say, at the equator)
    R = 6364465
    #Now we need to convert the coordinates to radians
    lat1, long1 = np.pi* coord1[0] /180 , np.pi *coord1[1]/180
    lat2, long2 = np.pi *coord2[0] /180 , np.pi *coord2[1] /180
    difflat = lat2 - lat1
    difflong = long2 - long1
    #Now calc haversine

    return 2*R*np.arcsin(np.sqrt(np.sin(difflat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(difflong/2)**2))

    
class order():
    def __init__(self,orderid :str, location: location, volume, value, time_required, shipping_date ):
        self.orderid = orderid
        self.location = location
        self.volume = volume
        self.value = value
        self.time_required = time_required
        self.shipping_date = shipping_date
    
    def __str__(self):
        return self.orderid + ' ' + str(self.location) + ' ' + str(self.volume) + ' ' + str(self.value) + ' ' + str(self.time_required) + ' ' + str(self.shipping_date) 


class route():
    def __init__(self, orderlist, totalDistance, estimatedTime,driver = 'Unassigned'):
        #Note that the orderlist is ORDERED. 
        self.orderlist = orderlist
        self.totalDistance = totalDistance
        self.estimatedTime = estimatedTime
        
def distanceMatrix(orderlist):
    #So we have a large list of N orders, we want an N*N matrix of distances between each order
    Dmat = np.zeros((len(orderlist), len(orderlist)))
    for i in range(len(orderlist)):
        for j in range(len(orderlist)):
            if i != j:
                Dmat[i,j] = distance(orderlist[i].location, orderlist[j].location)
    return Dmat



