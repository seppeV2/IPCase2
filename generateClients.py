import pandas as pd
from random import randrange

def generateClients(amount, csvCities):
    cities = pd.read_csv(csvCities)
    numberCities = len(cities.index)
    typesOfWaste = ['general','paper','construction','dangerous']
    containerSizes = [20,18,15,12,10,5]
    additionals = [0,0,0,0,15,20]
    
    dataHeader = ['ClientID','ClientName','ContainerSize','Waste','Place','ActionType','Additional','Opening','Closing']
    data = []

    for i in range(amount):
        city = cities.iloc[randrange(numberCities)]['name']
        waste = typesOfWaste[randrange(len(typesOfWaste))]
        containerSize = containerSizes[randrange(len(containerSizes))]
        additional = additionals[randrange(len(additionals))]
        actionType = randrange(6) + 1
        opening = 0
        closing = 600
        clientName = 'RandomClient_' + str(i)
        clienti = [i, clientName, containerSize, waste, city, actionType, additional, opening, closing]
        data.append(clienti)
    
    df = pd.DataFrame(data, columns = dataHeader)
    print(df)
    df.to_csv('randomClients.csv')
    return df

generateClients(200,'belgian-cities-geocoded.csv')
        
