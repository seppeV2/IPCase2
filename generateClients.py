import pandas as pd
from random import randrange
import os.path

def generateClients(amount, csvCities):
    cities = pd.read_csv('clients30.csv')
    cities=cities['Place']
    numberCities = len(cities.index)
    typesOfWaste = ['general','paper','construction','dangerous']
    containerSizes = [20,18,15,12,10,5]
    additionals = [0,0,0,0,15,20]
    
    dataHeader = ['ClientID','ClientName','ContainerSize','Waste','ActionType','Additional','opening','closing','Place']
    data = []
    for i in range(amount):
        # city = cities.iloc[randrange(numberCities)]['name']
        city = cities[randrange(len(cities))]
        waste = typesOfWaste[randrange(len(typesOfWaste))]
        containerSize = containerSizes[randrange(len(containerSizes))]
        additional = additionals[randrange(len(additionals))]
        actionType = randrange(5) + 1  # default 6
        if(actionType==6):
            # needs more thought
            opening = 999
            closing = 9999
            clientName = 'dangerousClient' + str(i)
        else:
            opening = 0
            closing = 600
            clientName = 'randomClient_' + str(i)
            
        clienti = [i+1, clientName, containerSize, waste, actionType, additional, opening, closing, city]
        data.append(clienti)
    
    df = pd.DataFrame(data, columns = dataHeader)
    df = df.set_index('ClientID')
    # df = df.iloc[: , 0:] # drop first column
    fileName='clients'+str(amount)+'.csv'
    if not os.path.isfile(fileName):
        df.to_csv(fileName)
        # print(df)
    return df

# generateClients(200,'belgian-cities-geocoded.csv')
    