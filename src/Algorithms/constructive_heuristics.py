#Use of exact methods is not actually feasible due to the size of the problem. So our implementation here will focus in heuristic methods. 

#Let's first try and implement a constructive heuristic - First we begin with a nearest neighbour heuristic - which is a greedy method.

#First to each vehicle we will attach a rout .
#2-Opt algorithm, which removes route crossings - good because drivers dont like to overleap routes
import numpy as np
import pandas as pd
from components import components as cp



def clarke_wright_savings(distance_matrix, demands, vehicle_capacity):
    """Solves CVRP using Clarke-Wright Savings Heuristic."""
    num_customers = len(distance_matrix) - 1  # Exclude depot (index 0)
    
    # Step 1: Compute Savings
    savings = []
    for i in range(1, num_customers + 1):
        for j in range(i + 1, num_customers + 1):
            save = distance_matrix[0][i] + distance_matrix[0][j] - distance_matrix[i][j]
            savings.append((save, i, j))
    savings.sort(reverse=True)  # Sort by descending savings

    # Step 2: Start with separate routes for each customer
    routes = {i: [i] for i in range(1, num_customers + 1)}
    route_loads = {i: demands[i] for i in range(1, num_customers + 1)}
    
    # Step 3: Merge routes based on savings
    for save, i, j in savings:
        if i in routes and j in routes and i != j:
            if route_loads[i] + route_loads[j] <= vehicle_capacity:
                # Merge routes
                routes[i].extend(routes[j])
                route_loads[i] += route_loads[j]
                del routes[j]

    # Step 4: Convert routes to include depot (0)
    final_routes = [[0] + route + [0] for route in routes.values()]
    return final_routes

# Example Usage
distance_matrix = np.array([
    [0, 10, 20, 30, 40],  
    [10, 0, 15, 25, 35],  
    [20, 15, 0, 10, 20],  
    [30, 25, 10, 0, 15],  
    [40, 35, 20, 15, 0]   
])
demands = [0, 2, 2, 2, 2]
vehicle_capacity = 4

routes = clarke_wright_savings(distance_matrix, demands, vehicle_capacity)
print("Generated Routes:", routes)