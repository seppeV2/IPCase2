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
            service = 12
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']

            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(newContractTo(clienti, clientj,cityNames)) + service
                
        elif clienti['ActionType'] == 2:
            service = 12
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(endContractTo(clienti, clientj,cityNames, wpf)) + service
               
        elif clienti['ActionType'] == 3:
            service = 12
            service += timeBetweenPlaces(clienti['Place'], closestPathWpf(clienti,clienti['Place'] ,wpf, cityNames)['Place'],cityNames)
            service += 20
            service += timeBetweenPlaces(closestPathWpf(clienti,clienti['Place'] ,wpf, cityNames)['Place'],clienti['Place'],cityNames)
            service += 12
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(sameContainerTo(clienti, clientj,cityNames)) + round(service)
                
        elif clienti['ActionType'] == 4:
            service = 25
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(switchTo(clienti, clientj,cityNames, wpf))  + service
        elif clienti['ActionType'] == 5:
            service = 30
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(fillingUpTo(clienti, clientj,cityNames, wpf)) + service
        elif clienti['ActionType'] == 6:
            service = 12
            service += timeBetweenPlaces(clienti['Place'], closestPathWpf(clienti,clienti['Place'], wpf, cityNames)['Place'],cityNames)
            service += 20
            service += timeBetweenPlaces(closestPathWpf(clienti, clienti['Place'] ,wpf, cityNames)['Place'],clienti['Place'],cityNames)
            service += 12
            if not pd.isnull(clienti['Additional']):
                service += clienti['Additional']
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(dangerousTo(clienti, clientj,cityNames)) + round(service)

    
    startMatrix = depotToClient(csvClientFile, cityNames)
    distanceMatrix = np.append(startMatrix, distanceMatrix,axis=1)
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

def closestPathWpf(clientNow, afterWpfDestination ,WPF, cityNames):
    wpf = pd.read_csv(WPF)
    waste = clientNow['Waste']
    place1 = clientNow['Place']
    distance = 0
    closest = None
    for i in range(len(wpf.index)):
        if distance == 0 and wpf.iloc[i][waste] == 'T':
            distance = timeBetweenPlaces(place1, wpf.iloc[i]['Place'], cityNames)
            closest = wpf.iloc[i]
        elif distance != 0:
            if (timeBetweenPlaces(clientNow['Place'], wpf.iloc[i]['Place'], cityNames) < distance) and wpf.iloc[i][waste] == 'T':
                distance = timeBetweenPlaces(place1, wpf.iloc[i]['Place'], cityNames)
                closest = wpf.iloc[i]
    return closest

#new contract
def newContractTo(clientNow, clientNext,cityNames):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return time
        
#end of contract
def endContractTo(clientNow, clientNext,cityNames, wpf):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #end of contract to new contract
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'],closestWpf , cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 2:
        #end of contract to end of contract
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #end of contract to exact same
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #end of contract to switch
    
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 5:
        #end of contract to fill up 
        
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #go to new client
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 6:
        #end of contract to dangerous
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return time

#exact same (equals new contract)
def sameContainerTo(clientNow, clientNext,cityNames):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return time

#switch (equals end of contract)
def switchTo(clientNow, clientNext,cityNames, wpf):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #switch to new contract
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'],closestWpf , cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 2:
        #switch to end of contract
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #switch to exact same
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #switch to switch
    
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 5:
        #switch to fill up 
        
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #go to new client
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 6:
        #switch to dangerous
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return time

#filling up (equals end of contract)
def fillingUpTo(clientNow, clientNext,cityNames, wpf):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #filling up to new contract
        #new container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #no new container size needed
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'],closestWpf , cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 2:
        #filling up to end of contract
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 3:
        #filling up to exact same
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    elif stateNext == 4:
        #filling up to switch
    
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout',wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 5:
        #filling up to fill up 
        
        #if other container size needed
        if clientNow['ContainerSize'] != clientNext['ContainerSize']:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #than go to depot 
            time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
            #change container 
            time += 6
            #go to new client
            time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
        #if not
        else:
            #first go to closest wpf
            closestWpf = closestPathWpf(clientNow, clientNext['Place'], wpf, cityNames)['Place']
            time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
            #empty the truck 
            time += 20
            #go to new client
            time+= timeBetweenPlaces(closestWpf, clientNext['Place'],cityNames)
    elif stateNext == 6:
        #filling up to dangerous
        #first go to closest wpf
        closestWpf = closestPathWpf(clientNow, 'Kampenhout', wpf, cityNames)['Place']
        time += timeBetweenPlaces(clientNow['Place'], closestWpf, cityNames)
        #empty the truck 
        time += 20
        #than go to depot 
        time += timeBetweenPlaces(closestWpf, 'Kampenhout', cityNames)
        #leave the container 
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'], cityNames)
    return time

#dangerous to (equals exact the same)
def dangerousTo(clientNow, clientNext,cityNames):
    time = 0
    stateNext = clientNext['ActionType']
    if stateNext == 1:
        #new contract to new contract 
        #first go to depot after new container (depot is in Kampenhout)
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 2:
        #new contract to end of contract
        #directly form client one to client two after
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 3:
        #new contract to exact same container
        #directly to client one to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    elif stateNext == 4:
        #new contract to switch
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 5:
        #new contract to filling up
        #first to depot after new container
        time+= timeBetweenPlaces(clientNow['Place'], 'Kampenhout', cityNames)
        #load new container onto truck
        time += 6
        #go to new client
        time += timeBetweenPlaces('Kampenhout', clientNext['Place'],cityNames)
    elif stateNext == 6:
        #new contract to dangerous waste 
        #directly to client
        time += timeBetweenPlaces(clientNow['Place'], clientNext['Place'], cityNames)
    return time

#makes an array with the time between depot and the first client 
def depotToClient(csvClient, cityNames):
    clients = pd.read_csv(csvClient)
    depotToStart = np.zeros([len(clients.index),1])
    for i in range(len(clients.index)):
        depotToStart[i,0] = round(timeBetweenPlaces('Kampenhout' , clients.iloc[i]['Place'], cityNames))
    
    return depotToStart

#makes an array with the time between last client and depot
def lastToDepot(csvClient, WPF , cityNames):
    clients = pd.read_csv(csvClient)
    wpf = pd.read_csv(WPF)
    lastToDepot = np.zeros([(len(clients.index)+len(wpf.index)),2])
    for i in range((len(clients.index)+len(wpf.index))):
        if i < len(clients.index):
            lastToDepot[i,0] = clients.iloc[i]['ClientID']
            lastToDepot[i,1] = round(timeBetweenPlaces( clients.iloc[i]['Place'], 'Kampenhout' ,cityNames))
        else:
            lastToDepot[i,0] = wpf.iloc[(i-len(clients.index))]['WPFid']
            lastToDepot[i,1] = round(timeBetweenPlaces( wpf.iloc[(i-len(clients.index))]['Place'], 'Kampenhout' ,cityNames))
    return lastToDepot

matrix = createDistanceMatrix('clientsTest.csv', 'belgian-cities-geocoded.csv', 'WPF.csv')
pd.DataFrame(matrix).to_csv('distanceMatrix.csv')

