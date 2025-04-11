import numpy as np 
import pulp
import matplotlib.pyplot as plt


def solve_cvrp_with_pulp(Dmatrix, capacity, fleetsize, ordersizes):
    """
    Shall solve CVRP using PuLP
    The depot index is taken to be zero
    """
    #n will be the number of locations
    n = len(Dmatrix)
    #moreover, we check if we have sufficient capacity
    if capacity*fleetsize < sum(ordersizes):
        print('Insufficient vehicles')
        return


    # Next, we the model in Pulp
    model = pulp.LpProblem("CVRP", pulp.LpMinimize)
    
    # and create our  x variables
    # x[i,j,k] = 1 if vehicle k travels from node i to node j
    #We initialise x as a dictionary, as opposed to an F x n x n matrix, as the latter is more finicky!
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:  # No self-loops
                for k in range(fleetsize):
                    x[i, j, k] = pulp.LpVariable(f"x_{i}_{j}_{k}", cat=pulp.LpBinary)
    
    # u[i] = cumulative demand after visiting node i, we are using MTZ subtour elimination here.
    u = {}
    for i in range(1, n):  
        u[i] = pulp.LpVariable(f"u_{i}", lowBound=ordersizes[i], upBound=capacity)
    


    # Objective: minimize total distance
    model += pulp.lpSum(Dmatrix[i][j] * x[i, j, k] 
                       for i in range(n) for j in range(n) for k in range(fleetsize) 
                       if i != j)
    
    # Now we implement the constraints that we chatted about in the notebook.
    # Each customer must be visited exactly once
    for j in range(1, n):  # For each customer (excluding depot)
        model += pulp.lpSum(x[i, j, k] for i in range(n) if i != j 
                           for k in range(fleetsize)) == 1
    
    # Each vehicle that enters a node must exit it
    for h in range(n):
        for k in range(fleetsize):
            model += pulp.lpSum(x[i, h, k] for i in range(n) if i != h) == \
                    pulp.lpSum(x[h, j, k] for j in range(n) if j != h)
    
    # Each vehicle starts and ends at depot
    for k in range(fleetsize):
        model += pulp.lpSum(x[0, j, k] for j in range(1, n)) <= 1  # Start
        model += pulp.lpSum(x[i, 0, k] for i in range(1, n)) <= 1  # End
    

    # Subtour elimination using MTZ 
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                for k in range(fleetsize):
                    model += u[i] - u[j] + capacity * x[i, j, k] <= capacity - ordersizes[j]
    
    # Capacity constraints
    for k in range(fleetsize):
        model += pulp.lpSum(ordersizes[j] * x[i, j, k] 
                           for i in range(n) for j in range(1, n) if i != j) <= capacity
    
    # And then pulp does the rest
    solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=300)  # have set a 5-minute time limit
    model.solve(solver)
    
    # Okay, so the solution is given to us as a big matrix x, we now convert this into some routes, which are just ordered lists for each one.
    routes = []
    #Only do if we've found an opti solution!
    if model.status == pulp.LpStatusOptimal:
        for k in range(fleetsize):
            #Loop thru
            route = [0]
            current = 0
            route_complete = False
            
            while not route_complete:
                for j in range(n):
                    if j != current and pulp.value(x[current, j, k]) > 0.5:
                        route.append(j)
                        current = j
                        break
                
                if current == 0:
                    route_complete = True
                elif not any(pulp.value(x[current, j, k]) > 0.5 for j in range(n) if j != current):
                    # This shouldn't happen in a valid solution, but just in case we've added this case. 
                    route.append(0)
                    route_complete = True
            
            if len(route) > 2: 
                routes.append(route)
    
    return model, routes



#Below we give an example: 
if __name__ == "__main__":
    #Generate random coordinates for nodes with 5 customers 
    np.random.seed(41) 
    num_customers = 5
    #Choose some coords in range 0, to 10 
    coordinates = np.random.rand(num_customers + 1, 2) * 10  
    # init distance matrix
    n = len(coordinates)
    Dmatrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[j]
                Dmatrix[i][j] = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    #set order sizes
    ordersizes = [0] + [5, 7, 3, 8, 4]  
    
    capacity = 15
    fleetsize = 2
    

    model, routes = solve_cvrp_with_pulp(
        Dmatrix=Dmatrix,
        capacity=capacity,
        fleetsize=fleetsize,
        ordersizes=ordersizes
    )
    
    #Now we print the outcomes from PuLP
    #if tis optimal we say so, then proceed
    print(f"Status: {pulp.LpStatus[model.status]}")

    if model.status == pulp.LpStatusOptimal:
        total_distance = pulp.value(model.objective)
        print(f"Total distance: {total_distance:.2f}")
        
        print("\nRoutes:")
        for i, route in enumerate(routes):
            route_demand = sum(ordersizes[j] for j in route if j != 0)
            route_distance = sum(Dmatrix[route[i]][route[i+1]] for i in range(len(route)-1))
            print(f"Vehicle {i+1}: {route} (Demand: {route_demand}/{capacity}, Distance: {route_distance:.2f})")
    
    # Next use some pyplot to visualise this 
    def plot_routes(coordinates, routes):
        plt.figure(figsize=(10, 8))
        
        # Plot all nodes
        #First one is the depot - give this a nice special marker
        plt.scatter(coordinates[0, 0], coordinates[0, 1], c='red', s=100, marker='^', label='Depot')
        #Then the rest. 
        plt.scatter(coordinates[1:, 0], coordinates[1:, 1], c='blue', s=50, label='Customers')
        
        # Add node labels
        for i in range(len(coordinates)):
            plt.annotate(f"{i}", (coordinates[i, 0] + 0.1, coordinates[i, 1] + 0.1))
        
        # Plot routes with different colors - Here we know that there wont be many routes - but I like our kinda gradient ipmlementation
        colours = [(( 255- x)/255, x/255,0 )  for x in np.linspace(0,255,len(routes))]

        for i, route in enumerate(routes):
            route_coords = coordinates[route]
            plt.plot(route_coords[:, 0], route_coords[:, 1], 
                     color=colours[i % len(colours)], linewidth=2, 
                     label=f"Vehicle {i+1}")
        
        plt.title(f"CVRP Solution - {len(routes)} vehicles, Total Distance: {total_distance:.2f}")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    if model.status == pulp.LpStatusOptimal:
        plot_routes(coordinates, routes)


