# IPCase2
The goal is to pre proses the client data before making the planning. 
The result of is a distance matrix (value = minutes). 

Each distance is calculated according the state of the current client and the state of the next client. 
states are defined as followed:     1 = new contract 
                                    2 = end contract 
                                    3 = exact same container
                                    4 = switch container 
                                    5 = filling `   up
                                    6 = dangerous waste

The depot is always situated in Kampenhout and the closest suitable wpf is used. 

For each element on the diagonal, the service time of client i is shown (matrix[i,i] = service time for i).
Service time = time spend at the costumer. 




after depot: do whatever you want.

at wpf: we unload without taking the containr off, no need to calculate additional 12 min.

if you can go direct, don't think about depot in the distance matrix!

## possible courses of actions and their total service time
### STARTING FROM END OF ACTIONTYPE 1,3
- 1-1: 
    - $$1-1 : idj = t_{id} + 6 + t_{dj} + 12 + EXTRA$$
- 1-2
    - $$1-2 : ij = t_{ij} + 12 + EXTRA$$
- 1-3
    - $$1-3: ijwj = t_{ij} + 12 + t_{jw} + 20 + t_{wj} + 12 + EXTRA$$
- 1-4
    - $$1-4 : idj = t_{id} + 6 + t_{dj} + 25 + EXTRA$$
- 1-5
    - $$1-5 : idj = t_{id} + 6 + t_{dj} + 30 + EXTRA$$
- 1-d
    - $$1-d : id = t_{id}$$
- 3: same as 1 : both start unloaded (empty)

### STARTING FROM END OF ACTIONTYPE 2,4,5
- 2-1
    - $$2-1 \& RS : iwj = t_{iw} + 20 + t_{wj} + 12 + EXTRA$$
    - $$2-1 \& WS : iwdj = t_{iw} + 20 + t_{wd} + 2*6 + t_{dj} + 12 + EXTRA$$
- 2-2
    - $$2-2 : iwdj = t_{iw} + 20 + t_{wd} + 6 + t_{dj} + 12 + EXTRA$$
- 2-3:
    - $$2-3 : iwdjwj: t_{iw} + 20 + t_{wd} + 6 + t_{dj} + 12 + t_{jw} + 20 + t_{wj} + 12 + EXTRA$$
- 2-4:
    - $$2-4 \& RS : iwj = t_{iw} + 20 + t_{wj} + 25 + EXTRA$$
    - $$2-4 \& WS : iwdj = t_{iw} + 20 + t_{wd} + 2*6 + t_{dj} + 25 + EXTRA$$
- 2-5: very similar to 2-4
    - $$2-5 \& RS : iwj = t_{iw} + 20 + t_{wj} + 30 + EXTRA$$
    - $$2-5 \& WS : iwdj = t_{iw} + 20 + t_{wd} + 2*6 + t_{dj} + 30 + EXTRA$$
- 2-d:
    - $$2-d : iwd = t_{iw} + 20 + t_{wd} + 6$$
- 4: same as 2 : both start loaded & full
- 5: same as 2 : both start loaded & full

### STARTING FROM DEPOT
- $$d-1 : dj = 6 + t_{dj} + 12 + EXTRA$$
- $$d-2 : dj = t_{dj} + 12 + EXTRA$$
- $$d-3 : djwj = t_{dj} + 12 + t_{jw} + 20 + t_{wj} + 12 + EXTRA$$
- $$d-4 : dj =  6 + t_{dj} + 25 + EXTRA$$
- $$d-5 : dj = 6 + t_{dj} + 30 + EXTRA$$

We have only 10 first-level pairs. As we care about the following pair:
$[endState_i,actionType_{j}]$

Then we consider size for 3 of them (when you start loaded & full): **13 in total**

Lastly, dangerous waste or other conditions, can be considered for the wpf. They don't have a nest of their own.

**ASSMPTION: trucks always start/end the day empty. all containers should be placed in depot not on trucks**

## how to enumerate the matrix
for each course of action, several routes might be available. we store them, and choose the "shortest path".

These possiblites are "per available customer_j". So, 1-5 means if you finish at actionType 1 (state Empty), there is only 1 route per customer of actionType 5 (your next step).

1-1: 1 
1-2: 1
1-3: #wpfs available
1-4: 1
1-5: 1

2-1RS: #w available
2-1WS: #w available
2-2: #w
2-3: #w@i * #w@j
2-4RS: #w
2-4WS: #w
2-5RS: #w
2-5WS: #w

then for all clients, we consider the values above.



### Now how to define number of wpfs available? (#w)?
if i = dangerous : only antwerp (w=1)
if i = construction : all (w=4)
if i = rest : mechelen,brugge,gent (w=3)

### some toy examples:
we are done with first customer, and want to calculate service time for another one.
bookstore20 to fish20: 
3-4 = 1-4:
only one value


[construction 18, lab 15]


[lab 10, end 12]


## HOW TO DEAL with end of tour?
if there are no feasible customers in the distance matrix, go back to depot and end your tour. feasiblity can be time cosntraint, fuel, work, etc.

## HOW TO STRUCTURE THE CODE?
```python
getNodes(database) {
    # here we save each node in JSON or sth, where we can access its attributes.
    # these nodes (clients / depot) will be used in later functions.

    node = {
        'ID', ..., #0 is depot, minus values for wpfs;   the rest are clients. 
        'coordinates', [x,y], # getX and getY: this can be taken from googlemaps API
        'actionType',1 to 5, # 1: new cont. 2: end cont. 3: exact same 4: swap 5: fill  ; is 0 for non-clients
        'containerSize',..., # whateever integer value ; is 0 for non-clients
        'wasteType', ..., #1:general 2: paper 3:const 4:dangerous ; is 0 for non-clients
        'wasteTypesHandled',... , # 0 for non-wpfs;   an array of wastetypes handled for wpfs. e.g. antwerp is dangerous only [4]
        'opening',..., #starting time window
        'closing ',..., #closing time window
        'extraHandling',..., #0 if none; int if needed (e.g. 15)
        ...
    }
}
# I THINK THE CODE ABOVE IS ALREADY IMPLEMENTED VIA PANDAS, THIS IS JUST TO GIVE AN IDEA

getShortestServiceTime(node_i,node_j) {
    # for depot
    # consider depot as customer with ID = 0
    # first check ID=0, to see if it's depot
    # here we consider services times starting from/end at depot:   d-x, or x-d


    # for all nodes (clients)
    # we get the following attributes from the client_i and client_j : ID
    # first check ID!=0, to make sure it's not depot
    # if not depot: get following attricuts containerSize, Location, actionType, wasteType
    ...
    # now we implement the conditions here, so that we can finally return a "serviceTime"
    # the idea is to use these attributes to implement the formulas
    # e.g. dangerous waste can be just an if statement inside one of the courses of action.


    # at the end we select the shortest service time (path) from i to j, and return it;
    # the output will be added to our pre-procssed distance matrix.
}

createDistanceMatrix {
    # here we iterate over all i and j, and fill in the shortest service time value inside it.
    # the values, are already taking into consideration all possible intermediate steps, and the shortest one is already selected.
}

```