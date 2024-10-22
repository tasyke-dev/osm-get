import osmnx as ox
import pandas as pd
import numpy as np
import csv
import requests
import re

countriesListforOSM = ['Algeria']
countriesListforDatasets = ['Algeria']

def removeBrackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) 
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: 
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close 
                if count[kind] < 0:
                    count[kind] = 0 
                else: 
                    break
            else: 
                if not any(count):
                    saved_chars.append(character)
    return ''.join(saved_chars)

for i in range(len(countriesListforOSM)):
    countryforLink = countriesListforDatasets[i]
    country_ = countriesListforOSM[i]
    URL = ("https://www.citypopulation.de/en/" + countryforLink.lower() + "/cities/")
    #URL = ("https://www.citypopulation.de/Libya.html")
    print(URL)
    dfs = pd.read_html(URL)
    a = dfs[2].columns.tolist()
    b = len(a)
    new_list = []
    s = 'PopulationCensus'
for i in range(b):
    f = a[i].find(s)
    if f != -1:
        new_list.append(a[i])
        populationColumn = new_list[-1]
        
        datainfo = dfs[2]
        datacols = ['Name', populationColumn]

        datainfo = datainfo[datacols]
        datainfo = datainfo.set_axis(['Name', 'population'], axis=1, inplace=False)
        for i in range(len(datainfo['Name'].values)):
                datainfo['Name'].values[i] = removeBrackets(datainfo['Name'].values[i])
                datainfo['Name'].values[i] = datainfo['Name'].values[i].replace(" ", "")
                tags = {"building": True}
                city_ = datainfo['Name'].tolist()
                citiesLength = len(city_)
                citiesLength -= 1
                while citiesLength > 0:
                    place = "%s, %s" % (city_[citiesLength], country_)
                    res = "%s.csv" % (city_[citiesLength])
                    curcity = (city_[citiesLength])
                    if (datainfo[datainfo.Name==curcity].size != 0):
                        try:
                            population = datainfo[datainfo.Name==curcity].population.item()
                        except Exception as e:
                            print(e)
                            citiesLength -= 1
                            continue
                        population = pd.to_numeric(population, errors='coerce')
                    else:
                        citiesLength -= 1
                        continue

                    print(place)
                    print(res)
                    try:
                        gdf = ox.geometries_from_place(place, tags)
                    except Exception as e:
                        print(e)
                        citiesLength -= 1
                        continue

                    gdf = gdf.to_crs(epsg=3395, inplace=False)
                    gdf['newarea'] = gdf['geometry'].area
                    gdf['population'] = population

                    gdf['total'] = gdf['newarea'].sum()
                    gdf['average'] = gdf.population / gdf.total
                    gdf['peopleInHouse'] = (gdf.newarea * gdf.average).apply(np.ceil)
                    gdf['allPeople'] = gdf['peopleInHouse'].sum()
                    cols = ['building', 'newarea', 'peopleInHouse', 'allPeople', 'total', 'average', 'population']
                    try:
                        result = gdf[cols]
                    except Exception as e:
                        print(e)
                        citiesLength -= 1
                        continue
                    result.to_csv(res, sep='\t', encoding='utf-8')
                    citiesLength -= 1
