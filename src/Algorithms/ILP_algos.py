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
    
    # Okay, so the solution is given to us as a big matrix x
    print(type(x))
    routes = []
    if model.status == pulp.LpStatusOptimal:
        for k in range(fleetsize):
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
                    # This shouldn't happen in a valid solution, but just in case
                    route.append(0)
                    route_complete = True
            
            if len(route) > 2:  # Only include non-empty routes
                routes.append(route)
    
    return model, routes



# Example usage
if __name__ == "__main__":
    # Create a sample problem with 5 customers + depot
    
    # Generate random coordinates for nodes
    np.random.seed(41)  # For reproducibility
    num_customers = 5
    coordinates = np.random.rand(num_customers + 1, 2) * 10  # Depot + 5 customers
    
    # Calculate distance matrix
    n = len(coordinates)
    Dmatrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[j]
                Dmatrix[i][j] = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Define order sizes (demand) - depot has demand 0
    ordersizes = [0] + [5, 7, 3, 8, 4]  # Depot + 5 customers
    
    # Set capacity and fleet size
    capacity = 15
    fleetsize = 2
    
    # Solve the problem
    model, routes = solve_cvrp_with_pulp(
        Dmatrix=Dmatrix,
        capacity=capacity,
        fleetsize=fleetsize,
        ordersizes=ordersizes
    )
    
    # Print results
    print(f"Status: {pulp.LpStatus[model.status]}")
    if model.status == pulp.LpStatusOptimal:
        total_distance = pulp.value(model.objective)
        print(f"Total distance: {total_distance:.2f}")
        
        print("\nRoutes:")
        for i, route in enumerate(routes):
            route_demand = sum(ordersizes[j] for j in route if j != 0)
            route_distance = sum(Dmatrix[route[i]][route[i+1]] for i in range(len(route)-1))
            print(f"Vehicle {i+1}: {route} (Demand: {route_demand}/{capacity}, Distance: {route_distance:.2f})")
    
    # Visualize the solution
    def plot_routes(coordinates, routes):
        plt.figure(figsize=(10, 8))
        
        # Plot all nodes
        plt.scatter(coordinates[0, 0], coordinates[0, 1], c='red', s=100, marker='s', label='Depot')
        plt.scatter(coordinates[1:, 0], coordinates[1:, 1], c='blue', s=50, label='Customers')
        
        # Add node labels
        for i in range(len(coordinates)):
            plt.annotate(f"{i}", (coordinates[i, 0] + 0.1, coordinates[i, 1] + 0.1))
        
        # Plot routes with different colors
        colors = ['green', 'orange', 'purple', 'brown', 'pink']
        for i, route in enumerate(routes):
            route_coords = coordinates[route]
            plt.plot(route_coords[:, 0], route_coords[:, 1], 
                     color=colors[i % len(colors)], linewidth=2, 
                     label=f"Vehicle {i+1}")
        
        plt.title(f"CVRP Solution - {len(routes)} vehicles, Total Distance: {total_distance:.2f}")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    if model.status == pulp.LpStatusOptimal:
        plot_routes(coordinates, routes)


