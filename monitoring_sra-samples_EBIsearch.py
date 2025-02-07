#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from centres import UiO_list, NTNU_list, UiB_list, NMBU_list, UiT_list, FHI_list #lists
from centres import centres #dictionary  

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
def standardise_centre(df):
    for centre in centres.keys(): 
        df.loc[df["center_name"].isin(centres[centre]), "center_name"] = centre
    return df
    
# get all the data
points_perpage = 1000 # max allowed by API
n_pages = get_dataset_size()//points_perpage # pages to get the whole database
fields = ["center_name","last_updated_date"] # fields for plotting
entries = get_entries(points_perpage,n_pages,fields)

# polish the data
df=pd.DataFrame(entries) 
fields = pd.json_normalize(df["fields"])
for column in fields.columns:
    df[column] = fields[column]
    df[column] = df[column].apply(lambda x: x[0] if len(x) > 0 else None)
df = df.drop(["source","acc","fields"], axis=1) # clean the dataframe to minimise output
df = df.set_index("id") # index by id for possible cross-referencing
df["last_updated_date"] = df["last_updated_date"].astype("datetime64[ns]")# change type to datetime
df=standardise_centre(df)
df=df[df["center_name"].isin(["UiO","UiB","UiT","NMBU","NTNU","FHI"])] # filter data from Norwegian inst.
df=df.dropna().sort_index() # remove lines with missing data and sort by index (id)
df.to_csv("data/data.csv")

# Grouping the data to plot into a unique dataframe, setting to 0. entries lacking data
#data2plot={}
#for centre in centres.keys():
#    data2plot[centre]=fields[fields["center_name"]==centre].groupby(fields["last_updated_date"].dt.year).count()["center_name"]
#data2plot = pd.DataFrame(data2plot)
#
#for centre in data2plot.columns:
#    data2plot[centre] = [0 if np.isnan(value) else value for value in data2plot[centre]]
#    data2plot[centre]=data2plot[centre].astype(int)
#data2plot.index=data2plot.index.astype(int)
#
# stacked-bars plot universities
#fig, ax = plt.subplots()
#
#bottom = 0.
#for centre in data2plot.columns:
#    if centre!="FHI":
#        ax.bar(data2plot.index, data2plot[centre], bottom = bottom, label=centre)
#        bottom=np.add(bottom, data2plot[centre])
#    
#plt.xlabel('YEAR')  # Set the label for the x-axis
#plt.ylabel('# samples submitted')  # Set the label for the y-axis
#plt.xticks(rotation=90)
#plt.xlim(2015.5, 2023.5)

#ax.legend()
#plt.savefig('./plots/stacked_bar_plot.png', bbox_inches='tight')
#
#fig, ax = plt.subplots()
#
# bar plot for FHI
#centre="FHI"
#ax.bar(data2plot.index, data2plot[centre], label=centre)
#bottom=np.add(bottom, data2plot[centre])
#    
#plt.xlabel('YEAR')  # Set the label for the x-axis
#plt.ylabel('# samples submitted')  # Set the label for the y-axis
#plt.xticks(rotation=90)
#plt.xlim(2015.5, 2023.5)
#
#ax.legend()
#plt.savefig('./plots/bar_plot_FHI.png', bbox_inches='tight')
