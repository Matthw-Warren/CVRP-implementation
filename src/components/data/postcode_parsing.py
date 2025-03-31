import pandas as pd

#OK, so I only really care about the postcode, and the coordintes of the given postcode. That is, the pcds (not 100% sure what the difference between pcd, pcds and pcd2 etc is, alas)
#So I want to import the relevant areas, To my mind set does deliveries to stockport, leeds, manchester, chester, Liverpool etc. 
# Looking at a postcode maps, we want to keep the following areas: 
postcode_areas = ['SK', 'LS', 'M', 'CH', 'L', 'CW', 'WA', 'WN', 'BL', 'OL', 'HD', 'HX','WF', 'BB', 'BD', 'PR', 'LA','ST' ]

#Now, we have large folder of postcode datas and want to pick the ones above out
pathroot = 'sample/data/ONSPD_FEB_2025_UK_'
#Empty lits of pandas dfs
df_list = []
for extension in postcode_areas:
    path = pathroot + extension + '.csv'
    df = pd.read_csv(path)[['pcd', 'lat','long']]
    df_list.append(df)

#Join all of these up.
data = pd.concat(df_list)

#Let's now save this as we'll be using it a decent amount!
data.to_csv('sample/data/postcodes_coords.csv', index=False)

