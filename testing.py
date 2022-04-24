import pandas as pd
import numpy as np

cities = pd.read_csv('belgian-cities-geocoded.csv')

antw = cities.loc[cities['name'] == 'Veurne']
print(antw.iloc[0]['province'])

#generates the distance between two places in belgium
def timeBetweenPlaces(Place1, Place2, cityNames):
    cities = pd.read_csv(cityNames)
    fromPlace = cities.loc[cities['name'] == Place1].iloc[0]
    toPlace = cities.loc[cities['name'] == Place2].iloc[0]

    #euclidian distance is used between the cooridantes (multiplied by 100)
    #these can be converted into real distances but this is not important at the moment
    distance = (((fromPlace['lat']-toPlace['lat'])**2 + (fromPlace['lng']-toPlace['lng'])**2)**0.5)*100
    return distance

#returns the closest compatible wpf
def closestWpf( WPF, cityNames):
    wpf = pd.read_csv(WPF)
    distance = timeBetweenPlaces('Veurne', wpf.iloc[1]['Place'], cityNames)
    closest = wpf.iloc[1]
    for i in range(len(wpf.index)-1):
        if ((timeBetweenPlaces('Veurne', wpf.iloc[i+1]['Place'], cityNames)) < distance) and wpf.iloc[i+1]['general'] == 'T':
            distance = (timeBetweenPlaces('Veurne', wpf.iloc[i+1], cityNames))
            closest = wpf.iloc[i+1]
    return closest

print(closestWpf('WPF.csv', 'belgian-cities-geocoded.csv')['Place'])