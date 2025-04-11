
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import os
import sys
from src.components import components as cp
from src.Algorithms import constructive_heuristics as ch

#src/components/data/postcodes_coords.csv
data = pd.read_csv('tests/postcodes_coords.csv')

#N the number of orders. 
N = 200

#Set the capcacity Q  and fleet size F 
Q = 60
F = 10


#data has 384,872 row and 3 columns. Let's generate a random sample of 500 order locations!
np.random.seed(15)
random_rows = np.random.randint(0, data.shape[0], 201)

#For each order we also want generate an id and a cost. Here the id's will just be 'ord001' to 'ord100', and the cost will be a random number between 10 and 100.
order_ids = ['ord' + str(i).zfill(3) for i in range(201)]
random_costs = np.random.randint(10,100,200)
random_volumes = np.random.randint(1,4,201)
random_volumes[0] = 0
random_locations = [cp.location(data.iloc[i,0], (data.iloc[i,1], data.iloc[i,2])) for i in random_rows]
depot_location = cp.location('M20 2XE', (53.422998567402104, -2.2503037071493703))
random_locations[0] = depot_location

Order_List = [cp.order('depot', depot_location,0,0,0, dt.datetime.now())]

for i in range(200):
    Order_List.append(cp.order(order_ids[i], random_locations[i+1], random_volumes[i+1], random_costs[i], 1, dt.datetime.now()))



#OKay - let's create a disance matrix,

Dmat = np.zeros((len(Order_List), len(Order_List)))
for i in range(len(Order_List)):
    for j in range(len(Order_List)):
        Dmat[i][j] = Order_List[i].location.distanceto(Order_List[j].location)

#Ok - lets run this thang. 
print(len(Order_List), len(Dmat), len(random_volumes))
routes, route_loads = ch.PNN_solve(Dmat, random_volumes, Q, F)
print('Routes:', routes)
print(sum(route_loads.values()))

#Intersting - many of the routes are empty - EVEN WITH parallel NN - so perhaps our fleet is far to large. 



#Going to save the data - and use for plotting on the map!?

import folium 



#We now create the map in folium
m = folium.Map(location=depot_location.coords)

# Add depot marker

folium.Marker(
    depot_location.coords,
    popup= f"Depot, Postcode = {depot_location.postcode}",
    icon=folium.Icon('blue', icon= 'Depot')
).add_to(m)

#Then add the rest!


for i, loc in enumerate([x.coords for x in random_locations]):
    folium.Marker(
        loc,
        popup=f"Customer {i+1}",
        icon=folium.Icon(color="blue", icon="home")
    ).add_to(m)

#Then we add the routes
for i, route in enumerate(routes.values()):
    scaled = int(i*255/F)
    colour = 'rgb(' + str(scaled) + ',' + str(255-scaled) + ',0)' 
    route_coords = [random_locations[i].coords for i in route]
    folium.PolyLine(
        locations=route_coords,
        color= colour,
        weight=5,
        opacity=0.7,
    ).add_to(m)

m.save("tests/folium_map.html")


