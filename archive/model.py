import sys
import math
import random
from itertools import permutations
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt

# tested with Python 3.7.0 & Gurobi 9.1.0



# number of locations, including the depot. The index of the depot is 0
n = 5
locations = [*range(n)]

# number of trucks
K = 3
trucks = [*range(K)]



# Create n random points
# Depot is located at (0,0) coordinates
random.seed(1)
points = [(0, 0)]
points += [(random.randint(0, 50), random.randint(0, 50)) for i in range(n-1)]

# Dictionary of Euclidean distance between each pair of points
# Assume a speed of 60 km/hr, which is 1 km/min. Hence travel time = distance
time = {(i, j):
        math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
        for i in locations for j in locations if i != j}

# big M
M = 1000 #TODO: to be changes


plt.scatter([x[0] for x in points], [x[1] for x in points])
plt.show()