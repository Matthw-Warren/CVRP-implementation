
import numpy as np
import pandas as pd
import datetime as dt


import os
import sys
from src.components import components as cp
from src.Algorithms import constructive_heuristics as ch

#src/components/data/postcodes_coords.csv
data = pd.read_csv('tests/postcodes_coords.csv')

#N the number of orders. 
N = 500

#Set the capcacity Q  and fleet size F 
Q = 60
F = 30


#data has 384,872 row and 3 columns. Let's generate a random sample of 500 order locations!
np.random.seed(15)
random_rows = np.random.randint(0, data.shape[0], 500)

#For each order we also want generate an id and a cost. Here the id's will just be 'ord001' to 'ord100', and the cost will be a random number between 10 and 100.
order_ids = ['ord' + str(i).zfill(3) for i in range(501)]
random_costs = np.random.randint(10,100,500)
random_volumes = np.random.randint(1,3,500)
random_locations = [cp.location(data.iloc[i,0], (data.iloc[i,1], data.iloc[i,2])) for i in random_rows]


Order_List = []

for i in range(500):
    Order_List.append(cp.order(order_ids[i], random_locations[i], random_volumes[i], random_costs[i], 1, dt.datetime.now()))

#OKay - let's create a disance matrix,

Dmat = np.zeros((len(Order_List), len(Order_List)))
for i in range(len(Order_List)):
    for j in range(len(Order_List)):
        Dmat[i][j] = Order_List[i].location.distanceto(Order_List[j].location)

#Ok - lets run this thang. 
print(len(Order_List), len(Dmat), len(random_volumes))
routes, route_loads = ch.SNN_solve(Dmat, random_volumes, Q, F)