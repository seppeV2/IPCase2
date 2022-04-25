# IPCase2
The goal is to pre proses the client data before making the planning. 
The result of is a distance matrix (value = minutes). 

Each distance is calculated according the state of the current client and the state of the next client. 
states are defined as followed:     1 = new contract 
                                    2 = end contract 
                                    3 = exact same container
                                    4 = switch container 
                                    5 = filling up
                                    6 = dangerous waste

The depot is always situated in Kampenhout and the closest suitable wpf is used. 

For each element on the diagonal, the service time of client i is shown (matrix[i,i] = service time for i).
Service time = time spend at the costumer. 