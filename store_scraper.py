'''
File:        FeedMe.py

Author(s):   Simon Corpuz (scorpuz)
             Bonnie Li (bonnieli)
             Suryaa Raman (ssuryaar)
             Yiyang Yao (yiyangya)

Imports:     Pandas
             Requests

Imported By: FeedMe.py

This file serves to download the map data from the Western Pennsylvania Regional
Data Center and convert it to a CSV format for the main application.
'''

import pandas as pd
import requests

# Function to download map data and convert to CSV
def download_stores(file="stores_default.csv"):
    url = "https://data.wprdc.org/dataset/690409e3-27e2-47a1-beed-fd600097f951/resource/626357fa-c95d-465f-9a02-3121655b2b78/download/data-conveniencesupermarkets.csv"
    response = requests.get(url)

    if response.status_code == 200:
        fin = open(file, "wb")
        fin.write(response.content)
    else:
        print("Failed to download CSV file. Status code:", response.status_code)

    stores = pd.read_csv(file)
    stores = stores[["Name", "Lat", "Lon", "Category"]]
    stores = stores.dropna()
    stores.to_csv(file)
