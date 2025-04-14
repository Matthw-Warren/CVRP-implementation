
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import os
import sys
from src.components import components as cp
from src.Algorithms import constructive_heuristics as ch
from src.Algorithms import intra_improvement_heuristics as ih
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




# #Ok - lets run this thang. 


"""PNN_solving"""

routes, route_loads = ch.PNN_solve(Dmat, random_volumes, Q, F)
for i in routes.keys():
    routes[i] = ih.exchange_improve(routes[i], Dmat)
print(routes)


"""SNN_solving"""

# routes ,route_loads = ch.SNN_solve(Dmat, random_volumes, Q, F)
# print('Routes:', routes) 



# #Going to save the data - and use for plotting on the map!?

"""SInsert_solving"""
# routes, route_loads = ch.SInsert_solve(Dmat, random_volumes, Q, F)
# print(routes)

"""PInsert_solving"""
# routes, route_loads = ch.PInsert_solve(Dmat, random_volumes, Q, F)
# print(routes)

"""CW_solve"""
#This has variable fleet size. 
# routes, route_loads= ch.CW_solve(Dmat, random_volumes, Q)
# for i in routes.keys():
#     routes[i] = ih.three_opt(routes[i], Dmat)
#     route_loads[i] = ih.two_opt(routes[i], Dmat)
# print(routes)


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
colourkeys = {0: 'red',1: 'green', 2: 'blue', 3: 'purple', 4: 'orange', 5: 'darkred', 6: 'yellow', 7: 'maroon', 8: 'darkblue', 9: 'darkgreen'}


for i, route in enumerate(routes.values()):
    print('Route:', route)
    colour = colourkeys[i]
    route_coords = [random_locations[j].coords for j in route]
    folium.PolyLine(
        locations=route_coords,
        color= colour,
        weight=5,
        opacity=0.7,
    ).add_to(m)




# Eventually in overlay want to toggle routes on and off!