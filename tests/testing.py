
import src.components as ods
import numpy as np
import pandas as pd
import datetime as dt


data = ods.pd.read_csv('sample/data/postcodes_coords.csv')
#data has 384,872 row and 3 columns. Let's generate a random sample of 100 order locations!
random_rows = np.random.randint(0, data.shape[0], 100)
#For each order we also want generate an id and a cost. Here the id's will just be 'ord001' to 'ord100', and the cost will be a random number between 10 and 100.
order_ids = ['ord' + str(i).zfill(3) for i in range(1,101)]
random_costs = np.random.randint(10,100,100)
random_volumes = np.random.randint(1,5,100)



random_locations = [ods.location(data.iloc[i,0], (data.iloc[i,1], data.iloc[i,2])) for i in random_rows]
