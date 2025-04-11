#Shall use folium to do the map visualisation.
import folium
import sys
import numpy as np
from src.components import components as cp
import pandas as pd
import datetime as dt


data = pd.read_csv('src/components/data/postcodes_coords.csv')


#Ok - So here we shall work with some sample data, but in reality we'd actually want our real coords.
# We'll use the same random seed as we did in testing.py
np.random.seed(15)
random_rows = np.random.randint(0, data.shape[0], 500)
#Shall again import the data.


#For each order we also want generate an id and a cost. Here the id's will just be 'ord001' to 'ord100', and the cost will be a random number between 10 and 100.
order_ids = ['ord' + str(i).zfill(3) for i in range(501)]
random_costs = np.random.randint(10,100,500)
random_volumes = np.random.randint(1,3,5000)
random_locations = [cp.location(data.iloc[i,0], (data.iloc[i,1], data.iloc[i,2])) for i in random_rows]

#We'll also initialise the depot location which we'd like to be at the centre of our map - shall set this as
depot_location = cp.location('M20 2XE', (53.422998567402104, -2.2503037071493703))



#We now create the map in folium
m = folium.Map(location=depot_location.coords)

# Add depot marker

folium.Marker(
    depot_location.coords,
    popup= f"Depot, Postcode = {depot_location.postcode}",
    icon=folium.Icon('blue', icon= 'Depot')
).add_to(m)

m.save('test.html')