#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import numpy as np

def get_api_url(n_size, j_page,fields):
    base = "https://www.ebi.ac.uk/ebisearch/ws/rest/sra-sample?query=country:Norway"
    api_url = base + "&size="+str(n_size)+"&start="+str(n_size*j_page)+"&fields="+','.join(fields)+"&format=json"
    return api_url

def get_dataset(api_url):
    response = requests.get(api_url)
    results = json.loads(response.content.decode())
    return(results)

def get_dataset_size():
    api_url = get_api_url(1,1,["center_name","last_updated_date"])
    results = get_dataset(api_url)
    return(results['hitCount'])

def get_entries(n_size,n_page,fields):
    entries=[]
    for j_page in range(n_pages+1):
        api_url=get_api_url(n_size, j_page, fields)
        data=get_dataset(api_url)
        entries.extend(data["entries"])
    if len(entries)!=get_dataset_size():
        print("WARNING: wrong number of entries: ", len(entries)," vs ", get_dataset_size(), " hits")
    return(entries)

# get all the data
points_perpage = 1000 # max allowed by API
n_pages = get_dataset_size()//points_perpage # pages to get the whole database
fields = ["center_name","last_updated_date"] # fields for plotting
entries = get_entries(points_perpage,n_pages,fields)

# polish the data for plotting
df=pd.DataFrame(entries) 
fields = pd.json_normalize(df["fields"]) # extract the variables for plotting
for column in fields.columns: # change from list to standard variable
    fields[column]=fields[column].apply(lambda x: x[0] if len(x) > 0 else None)
# change to proper date/time type 
fields["last_updated_date"] = fields["last_updated_date"].astype("datetime64[ns]")

# making the centre name smoother
UiO_list = [
    'University of Oslo',
    'UNIVERSITY OF OSLO',
    'University of Oslo, Department of Biosciences',
    'University of oslo',
    'Universitetet i Oslo',
    'Department of Paediatric Medicine, Oslo University Hospital',
    'Oslo University',
    'Unversity of Oslo',
    'Oslo University Hospital',
    'Insititute of Oral Biology, Univeristy of Oslo',
    'Oslo University Hospital, Rikshopitalet',
    'Archaeogenomics group, Department of Biosciences, University of Oslo',
    'Oslo University Hospital/University of Oslo',
    'OSLO UNIVERSITY HOSPITAL',
    'Department of Biosciences, University of Oslo',
    'Natural History Museum, University of Oslo',
    'UIO',
    'CEES'
]

NTNU_list = [
    'NTNU',
    'NTNU - Norwegian University of Science and Technology',
    'NTNU University Museum'
]

UiB_list = [
    'University of Bergen',
    'CENTRE FOR GEOBIOLOGY, DEPARTMENT OF BIOLOGY, UNIVERSITY OF BERGEN, NORWAY',
    'Universitetet i Bergen',
    'UNIVERSITY OF BERGEN/DEPT. OF BIOLOGY',
    'K.G. Jebsen center for deep-sea research, University of Bergen',
    'Center for Geobiology, University of Bergen',
    'UNIVERSITY OF BERGEN',
    'UiB'
]

NMBU_list = [
    'FACULTY OF CHEMISTRY, BIOTECHNOLOGY AND FOOD SCIENCE (IKBM), NORWEGIAN UNIVERSITY OF LIFE SCIENCES (NMBU), NORWAY',
    'NMBU Norwegian University of Life Sciences',
    'NMBU',
    'Norwegian University of Life Sciences (NMBU)',
]

UiT_list = [
    'University of Tromso',
    'UiT the Arctic University of Norway',
    'UiT: The Arctic University of Norway',
    'UiT, The Arctic University of Norway',
    'UIT',
    'UiT The Arctic University if Norway',
    'UiT The Arctic University',
    'UiT - The Arctic University of Norway',
    'The Arctic University of Norway',
    'University of Tromsoe',
    'Sletvold H., Department of Pharmacy, University of Tromso, Tromso, N-9037, NORWAY',
    'Tromsoe University Museum',
    'University of Tromso - The Arctic University of Norway',
    'UNIVERSITY OF TROMSO'
]

FHI_list=[
    'Norwegian Institute of Public Health (NIPH)',
    'NIPH',
    'NORWEGIAN INSTITUTE OF PUBLIC HEALTH',
    'Folkehelseinstituttet (FHI), Norway'
]

centres = {
    "UiO": UiO_list,
    "UiB": UiB_list,
    "UiT": UiT_list,
    "NMBU": NMBU_list,
    "NTNU": NTNU_list,
    "FHI": FHI_list
}

for centre in centres.keys(): 
    fields.loc[fields["center_name"].isin(centres[centre]), "center_name"] = centre

# Grouping the data to plot into a unique dataframe, setting to 0. entries lacking data
data2plot={}
for centre in centres.keys():
    data2plot[centre]=fields[fields["center_name"]==centre].groupby(fields["last_updated_date"].dt.year).count()["center_name"]
data2plot = pd.DataFrame(data2plot)

for centre in data2plot.columns:
    data2plot[centre] = [0 if np.isnan(value) else value for value in data2plot[centre]]
    data2plot[centre]=data2plot[centre].astype(int)
data2plot.index=data2plot.index.astype(int)

# stacked-bars plot universities
fig, ax = plt.subplots()

bottom = 0.
for centre in data2plot.columns:
    if centre!="FHI":
        ax.bar(data2plot.index, data2plot[centre], bottom = bottom, label=centre)
        bottom=np.add(bottom, data2plot[centre])
    
plt.xlabel('YEAR')  # Set the label for the x-axis
plt.ylabel('# samples submitted')  # Set the label for the y-axis
plt.xticks(rotation=90)
plt.xlim(2015.5, 2023.5)

ax.legend()
plt.savefig('stacked_bar_plot.png', bbox_inches='tight')

fig, ax = plt.subplots()

# bar plot for FHI
centre="FHI"
ax.bar(data2plot.index, data2plot[centre], label=centre)
bottom=np.add(bottom, data2plot[centre])
    
plt.xlabel('YEAR')  # Set the label for the x-axis
plt.ylabel('# samples submitted')  # Set the label for the y-axis
plt.xticks(rotation=90)
plt.xlim(2015.5, 2023.5)

ax.legend()
plt.savefig('bar_plot_FHI.png', bbox_inches='tight')
