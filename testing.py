import pandas as pd
import numpy as np

cities = pd.read_csv('belgian-cities-geocoded.csv')

client = pd.read_csv('clientsTest.csv')

print(pd.isnull(client.iloc[2]['Additional']))