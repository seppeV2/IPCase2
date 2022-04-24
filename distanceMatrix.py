import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians


def createDistanceMatrix(csvClientFile, cityNames, wpf):
    clients = pd.read_csv(csvClientFile)
    clientsAmount = len(clients.index)

    #initial zeros distance matrix
    distanceMatrix = np.zeros([clientsAmount,clientsAmount])

    for i in range(clientsAmount):
        #line form one client
        clienti = clients.iloc[i]
        if clienti['ActionType'] == 1:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(newContractTo(clienti, clientj,cityNames))
        elif clienti['ActionType'] == 2:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(endContractTo(clienti, clientj,cityNames, wpf))
        elif clienti['ActionType'] == 3:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(sameContainerTo(clienti, clientj,cityNames))
        elif clienti['ActionType'] == 4:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(switchTo(clienti, clientj,cityNames, wpf))
        elif clienti['ActionType'] == 5:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(fillingUpTo(clienti, clientj,cityNames, wpf))
        elif clienti['ActionType'] == 6:
            for j in range(clientsAmount):
                
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(dangerousTo(clienti, clientj,cityNames))
    print(distanceMatrix)
    return distanceMatrix
#calculate distance in km between two coordinates
def distanceKmFromCoord(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

#generates the distance between two places in belgium
def timeBetweenPlaces(Place1, Place2, cityNames):
    cities = pd.read_csv(cityNames)
    fromPlace = cities.loc[cities['name'] == Place1].iloc[0]
    toPlace = cities.loc[cities['name'] == Place2].iloc[0]

    distance = distanceKmFromCoord(fromPlace['lat'],fromPlace['lng'],toPlace['lat'],toPlace['lng'])
    averageTime = 50 
    #time = distance/speed (km/h) -> *60 to have minutes
    time = (distance / averageTime)*60
    return time

#returns the closest compatible wpf
def closestWpf(clientNow, WPF, cityNames):
    wpf = pd.read_csv(WPF)
    distance = timeBetweenPlaces(clientNow['Place'], wpf.iloc[0]['Place'], cityNames)
    closest = wpf.iloc[0]
    for i in range(len(wpf.index)-1):
        if ((timeBetweenPlaces(clientNow['Place'], wpf.iloc[i+1]['Place'], cityNames)) < distance) and wpf.iloc[i+1][clientNow['Waste']] == 'T':
            distance = (timeBetweenPlaces(clientNow['Place'], wpf.iloc[i+1]['Place'], cityNames))
            closest = wpf.iloc[i+1]
    return closest

#end of contract
def endContractTo(clientNow, clientNext,cityNames, wpf):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #end of contract to new contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 2:
        #end of contract to end of contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #end of contract to exact same
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #end of contract to switch
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 5:
        #end of contract to fill up 
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 6:
        #end of contract to dangerous
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return genTime

#exact same (equals new contract)
def sameContainerTo(clientNow, clientNext,cityNames):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return genTime

#switch (equals end of contract)
def switchTo(clientNow, clientNext,cityNames, wpf):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #end of contract to new contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 2:
        #end of contract to end of contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #end of contract to exact same
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #end of contract to switch
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 5:
        #end of contract to fill up 
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 6:
        #end of contract to dangerous
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return genTime

#filling up (equals end of contract)
def fillingUpTo(clientNow, clientNext,cityNames, wpf):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #end of contract to new contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 2:
        #end of contract to end of contract
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #end of contract to exact same
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #end of contract to switch
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 5:
        #end of contract to fill up 
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #than go to depot 
            genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
            #change container 
            genTime += 6
            #go to new client
            genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            genTime+= timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], clientNext['Place'],cityNames)
    elif stateNext == 6:
        #end of contract to dangerous
        #first go to closest wpf
        genTime += timeBetweenPlaces(clientNow['Place'], closestWpf(clientNow, wpf, cityNames)['Place'], cityNames)
        #empty the truck 
        genTime += 20
        #than go to depot 
        genTime += timeBetweenPlaces(closestWpf(clientNow, wpf, cityNames)['Place'], 'Kampenhout', cityNames)
        #leave the container 
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return genTime

#dangerous to (equals exact the same)
def dangerousTo(clientNow, clientNext,cityNames):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return genTime

def newContractTo(clientNow, clientNext,cityNames):
    genTime = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        genTime+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        genTime += 6
        #go to new client
        genTime += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        genTime += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return genTime
 
matrix = createDistanceMatrix('clientsTest.csv', 'belgian-cities-geocoded.csv', 'WPF.csv')
pd.DataFrame(matrix).to_csv('distanceMatrix.csv')

