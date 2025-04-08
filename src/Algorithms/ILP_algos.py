import numpy as np 
import pulp


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
    x = {}
    for i in range(n):
        for j in range(n):
            if i != j:  # No self-loops
                for k in range(fleetsize):
                    x[i, j, k] = pulp.LpVariable(f"x_{i}_{j}_{k}", cat=pulp.LpBinary)
    
    # u[i] = cumulative demand after visiting node i, we are using MTZ subtour elimination here!
    u = {}
    for i in range(1, n):  
        u[i] = pulp.LpVariable(f"u_{i}", lowBound=demands[i], upBound=capacity)
    

    
    # Objective: minimize total distance
    model += pulp.lpSum(distances[i][j] * x[i, j, k] 
                       for i in range(n) for j in range(n) for k in range(fleetsize) 
                       if i != j)
    
    # Constraints
    
    # 1. Each customer must be visited exactly once
    for j in range(1, n):  # For each customer (excluding depot)
        model += pulp.lpSum(x[i, j, k] for i in range(n) if i != j 
                           for k in range(fleetsize)) == 1
    
    # 2. Flow conservation: each vehicle that enters a node must exit it
    for h in range(n):
        for k in range(fleetsize):
            model += pulp.lpSum(x[i, h, k] for i in range(n) if i != h) == \
                    pulp.lpSum(x[h, j, k] for j in range(n) if j != h)
    
    # 3. Each vehicle starts and ends at depot
    for k in range(fleetsize):
        model += pulp.lpSum(x[depot_index, j, k] for j in range(1, n)) <= 1  # Start
        model += pulp.lpSum(x[i, depot_index, k] for i in range(1, n)) <= 1  # End
    
    # 4. Subtour elimination using MTZ constraints
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                for k in range(fleetsize):
                    model += u[i] - u[j] + capacity * x[i, j, k] <= capacity - demands[j]
    
    # 5. Vehicle capacity constraints
    for k in range(fleetsize):
        model += pulp.lpSum(demands[j] * x[i, j, k] 
                           for i in range(n) for j in range(1, n) if i != j) <= capacity
    
    # Solve the model
    solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=300)  # 5-minute time limit
    model.solve(solver)
    
    # Extract solution
    routes = []
    if model.status == pulp.LpStatusOptimal:
        for k in range(fleetsize):
            route = [depot_index]
            current = depot_index
            route_complete = False
            
            while not route_complete:
                for j in range(n):
                    if j != current and pulp.value(x[current, j, k]) > 0.5:
                        route.append(j)
                        current = j
                        break
                
                if current == depot_index:
                    route_complete = True
                elif not any(pulp.value(x[current, j, k]) > 0.5 for j in range(n) if j != current):
                    # This shouldn't happen in a valid solution, but just in case
                    route.append(depot_index)
                    route_complete = True
            
            if len(route) > 2:  # Only include non-empty routes
                routes.append(route)
    
    return model, routes




# def obj_function(Dmatrix, xmatrix):
#     #The xmatrix is going to be a matrix of size F * n^2- where F is fleetsize. 
#     sum = 0
#     for k in range(xmatrix.shape[0]):
#         sum += np.sum(np.multiply(Dmatrix,xmatrix[k])) 
#     return sum

# def path_constraint(Dmatrix, xmatrix):
    


# def ILP_solution(Dmatrix, orders, capacity, fleetsize) -> np.array:
#     #Ok, so we have some graph with our locations on, and the 0th node is our depo, the input variables are obviouly defined.
#     #See the jupyter for how this problem is setup as an ILP problem, to eliminate subroutes (ie, closed routes that dont visit the depot, we've used MTZ constraints)

#     pass



