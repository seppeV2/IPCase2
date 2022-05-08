from tracemalloc import start
import pandas as pd
import numpy as np
from generateClients import generateClients
from math import sin, cos, sqrt, atan2, radians
import time

def createDistanceMatrix(csvClientFile, cityNames, wpf):
    clients = pd.read_csv(csvClientFile)
    clientsAmount = len(clients.index)

    #initial zeros distance matrix (N by N)
    distanceMatrix = np.zeros([clientsAmount,clientsAmount])

    # row/column 1 to N are customers
    for i in range(clientsAmount):
        #line form one client
        clienti = clients.iloc[i]
        if clienti['ActionType'] == 1:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(newContractTo(clienti, clientj,cityNames)) + getServiceTime(clientj,cityNames,wpf)
                
        elif clienti['ActionType'] == 2:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(endContractTo(clienti, clientj,cityNames, wpf)) + getServiceTime(clientj,cityNames,wpf)
               
        elif clienti['ActionType'] == 3:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(sameContainerTo(clienti, clientj,cityNames)) + getServiceTime(clientj,cityNames,wpf)
                
        elif clienti['ActionType'] == 4:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(switchTo(clienti, clientj,cityNames, wpf))  + getServiceTime(clientj,cityNames,wpf)
                    
        elif clienti['ActionType'] == 5:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(fillingUpTo(clienti, clientj,cityNames, wpf)) + getServiceTime(clientj,cityNames,wpf)
        elif clienti['ActionType'] == 6:
            for j in range(clientsAmount):
                if i != j:
                    clientj = clients.iloc[j]
                    distanceMatrix[i,j] = round(dangerousTo(clienti, clientj,cityNames)) + getServiceTime(clientj,cityNames,wpf)

    # extending the matrix for depot 
    # row 0 is start: depot to customers
    startMatrix = depotToClient(csvClientFile, cityNames, wpf)
    distanceMatrix=np.vstack([startMatrix,distanceMatrix])

    # column 0 is finish: customers to depot
    endMatrix = np.c_[np.append(0, lastToDepot(csvClientFile, wpf, cityNames))]
    distanceMatrix=np.append(endMatrix,distanceMatrix,axis=1)

    # print(distanceMatrix)

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
    averageSpeed = 50 
    #time = distance/speed (km/h) -> *60 to have minutes
    time = (distance / averageSpeed)*60
    # print(Place1,Place2,time)
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
    print('WPFS: '+clientNow['Place'],distance,closest.Place,afterWpfDestination)
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
        # print(clientNext['Place'])
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
    print('1: ',clientNow.Place,clientNext.Place,time)
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
            time += 6*2
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
            time += 6*2
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
            time += 6*2
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
    print('2: ',clientNow.Place,clientNext.Place,time)
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
    print('3: ',clientNow.Place,clientNext.Place,time)
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
            time += 6*2
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
            time += 6*2
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
            time += 6*2
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
    print('4: ',clientNow.Place,clientNext.Place,time)
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
            time += 6*2
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
            time += 6*2
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
            time += 6*2
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
    print('5: ',clientNow.Place,clientNext.Place,time)
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
    print('6: ',clientNow.Place,clientNext.Place,time)
    return time

#makes an array with the time between depot and the first client 
def depotToClient(csvClient, cityNames, wpf):
    clients = pd.read_csv(csvClient)
    depotToStart = np.zeros([len(clients.index)])
    for i in range(len(clients.index)):
        clienti = clients.iloc[i]
        if clienti['ActionType'] == 1:
            #load the container
            timeFromDepot = 6
            #drive to the first client
            timeFromDepot += round(timeBetweenPlaces('Kampenhout' , clienti['Place'], cityNames))
            #allocate
            depotToStart[i] = timeFromDepot + getServiceTime(clienti,cityNames,wpf)
        elif clienti['ActionType'] == 4:
            #load the container
            timeFromDepot = 6
            #drive to the first client
            timeFromDepot += round(timeBetweenPlaces('Kampenhout' , clienti['Place'], cityNames))
            #allocate
            depotToStart[i] = timeFromDepot + getServiceTime(clienti,cityNames,wpf)
        elif clienti['ActionType'] == 5:
            #load the container
            timeFromDepot = 6
            #drive to the first client
            timeFromDepot += round(timeBetweenPlaces('Kampenhout' , clienti['Place'], cityNames))
            #allocate
            depotToStart[i] = timeFromDepot + getServiceTime(clienti,cityNames,wpf)
        elif clienti['ActionType'] == 2:
            #go with empty truck to first client
            timeFromDepot = round(timeBetweenPlaces('Kampenhout' , clienti['Place'], cityNames))  
            #allocate
            depotToStart[i] = timeFromDepot + getServiceTime(clienti,cityNames,wpf)
        elif clienti['ActionType'] == 3 or clienti['ActionType'] == 6:
            #go with empty truck to first client
            timeFromDepot = round(timeBetweenPlaces('Kampenhout' , clienti['Place'], cityNames))  
            #allocate
            depotToStart[i] = timeFromDepot + getServiceTime(clienti,cityNames,wpf)
    return depotToStart

#makes an array with the time between last client and depot
def lastToDepot(csvClient, WPF , cityNames):
    clients = pd.read_csv(csvClient)
    lastToDepot = np.zeros([(len(clients.index))])
    for i in range(len(clients.index)):
        clienti = clients.iloc[i]
        if clienti['ActionType'] == 2 or clienti['ActionType'] == 4 or clienti['ActionType'] == 5:
            #first go to best wpf than to depot
            bestWpf = closestPathWpf(clienti,'Kampenhout', WPF, cityNames)
            timeToDepot = round(timeBetweenPlaces( clienti['Place'], bestWpf['Place'] ,cityNames))
            #empty container
            timeToDepot += 20
            #go to depot
            timeToDepot += round(timeBetweenPlaces(bestWpf['Place'], 'Kampenhout', cityNames))
            #unload container
            timeToDepot += 6
            #allocate this to the matrix
            lastToDepot[i] = timeToDepot
        else:
            #go with empty truck to depot
            timeToDepot = round(timeBetweenPlaces(clienti['Place'], 'Kampenhout', cityNames))
            lastToDepot[i] = timeToDepot
    return lastToDepot

def getServiceTime(client, cityNames, wpf):
    state = client['ActionType']
    place = client['Place']
    if state == 1:
        #do the action at the fist client
            #unloading the container
        serviceTime = 12
            #extras
        serviceTime += client['Additional']   
        print('ST: @'+client['Place'],serviceTime)
        return round(serviceTime)  
    elif state == 4:
        #do the action at the fist client
            #swapping the container
        serviceTime = 25
            #extras
        serviceTime += client['Additional'] 
        print('ST: @'+client['Place'],serviceTime)  
        return round(serviceTime)  
    elif state == 5:
        #do the action at the fist client
            #filling the container
        serviceTime = 30
            #extras
        serviceTime += client['Additional']   
        print('ST: @'+client['Place'],serviceTime) 
        return round(serviceTime) 
    elif state == 2:
        #do the action at the fist client
            #loading the container
        serviceTime = 12
            #extras
        serviceTime += client['Additional']  
        print('ST: @'+client['Place'],serviceTime)  
        return round(serviceTime) 
    elif state == 3 or state == 6:
        #do the action at the fist client
            #loading the container
        serviceTime = 12
            #go to wpf
        bestWpf = closestPathWpf(client, place, wpf, cityNames)
        serviceTime += timeBetweenPlaces(place , bestWpf['Place'], cityNames)
            #empty the truck at wpf
        serviceTime += 20
            #go back to client 
        serviceTime += timeBetweenPlaces(bestWpf['Place'], place, cityNames)
            #unload the container
        serviceTime += 12
            #extras
        serviceTime += client['Additional']   
        print('ST: @'+client['Place'],serviceTime)
        return round(serviceTime) 

# start = time.time()
# matrix = createDistanceMatrix('clientsTest.csv', 'belgian-cities-geocoded.csv', 'WPF.csv')
# end = time.time()
