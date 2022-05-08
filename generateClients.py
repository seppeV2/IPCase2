import pandas as pd
from random import randrange
import os.path

def generateClients(amount, csvCities):
    cities = pd.read_csv(csvCities)
    numberCities = len(cities.index)
    typesOfWaste = ['general','paper','construction','dangerous']
    containerSizes = [20,18,15,12,10,5]
    additionals = [0,0,0,0,15,20]
    
    dataHeader = ['ClientID','ClientName','ContainerSize','Waste','Place','ActionType','Additional','opening','closing']
    data = []
    for i in range(amount):
        city = cities.iloc[randrange(numberCities)]['name']
        waste = typesOfWaste[randrange(len(typesOfWaste))]
        containerSize = containerSizes[randrange(len(containerSizes))]
        additional = additionals[randrange(len(additionals))]
        actionType = randrange(6) + 1
        if(actionType==6):
            # needs more thought
            opening = 360
            closing = 540-20
            clientName = 'dangerousPlace' + str(i)
        else:
            opening = 0
            closing = 600
            clientName = 'RandomClient_' + str(i)
            
        clienti = [i+1, clientName, containerSize, waste, city, actionType, additional, opening, closing]
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
    