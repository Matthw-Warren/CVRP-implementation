
import numpy as np
import pandas as pd
import datetime as dt

from context import src
import os
import sys
from src import components as cp


#src/components/data/postcodes_coords.csv
data = pd.read_csv('tests/postcodes_coords.csv')
print(data.head())  

#data has 384,872 row and 3 columns. Let's generate a random sample of 500 order locations!
random_rows = np.random.randint(0, data.shape[0], 500)
#For each order we also want generate an id and a cost. Here the id's will just be 'ord001' to 'ord100', and the cost will be a random number between 10 and 100.
#N the number of orders. 
N = 250

order_ids = ['ord' + str(i).zfill(3) for i in range(501)]
random_costs = np.random.randint(10,100,500)
random_volumes = np.random.randint(1,3,5000)
random_locations = [cp.location(data.iloc[i,0], (data.iloc[i,1], data.iloc[i,2])) for i in random_rows]

#Set the capcacity Q  and fleet size F 
Q = 50
F = 10

Order_List = []

for i in range(500):
    Order_List.append(cp.order(order_ids[i], random_locations[i], random_volumes[i], random_costs[i], 1, dt.datetime.now()))
