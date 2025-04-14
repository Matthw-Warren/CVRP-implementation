#Use of exact methods is not actually feasible due to the size of the problem. So our implementation here will focus in heuristic methods. 
import numpy as np
import pandas as pd
from src.components import components as cp
import src.Algorithms.intra_improvement_heuristics as ih



#Let's begin with  NN solutions

#Sequential NN - build one route at a time ( as opposed to parallel NN)
#Simplest method - could add customisations
#Most implementations are acutally more complex than this - moreover, should really implement lambda-opt improvement each time. 

def SNN_solve(Dmat, order_sizes, capacity, fleetsize):
    """CVRP solve using SNN heuristic"""
    if sum(order_sizes) > fleetsize*capacity:
        return 'Insufficient fleet'
    # Initialise the routes
    routes = {i: [0] for i in range(fleetsize)}
    route_loads = {i: 0 for i in range(fleetsize)}
    
    # Start from depot (0) and we shall add in vertices
    N = len(Dmat)  # Number of customers + depot
    unvisited = list(range(1, N))  # Customers to visit
    # Start with the first vehicle
    for vehicle in range(fleetsize):
        current_location = 0  # Start at depot
        route_loads[vehicle] = 0
        while route_loads[vehicle] < capacity and unvisited:
            nearest_customer = None
            nearest_distance = float('inf')
            #Then we look through the unvisited nodes to find the nearest. 
            for customer in unvisited:
                if Dmat[current_location][customer] < nearest_distance and route_loads[vehicle] + order_sizes[customer] <= capacity:
                    nearest_distance = Dmat[current_location][customer]
                    nearest_customer = customer
            if nearest_customer is not None:
                    # Add the nearest customer to the route
                    routes[vehicle].append(nearest_customer)
                    route_loads[vehicle] += order_sizes[nearest_customer]
                    unvisited.remove(nearest_customer)
                    current_location = nearest_customer
                    #Three opt at each change.
                    routes[vehicle] = ih.three_opt(routes[vehicle], Dmat)
            else:
                break
        #Then we return to the depot once this route is filled up. Not that even if there is a feasible route, this method may not even find it!
        #We'll elobrate in the insertion method - where we can add customers to any route, and not nec at the ends

        routes[vehicle].append(0)  # Return to depot
        #Could here do some optimisation - but again we're not there yet.
    return routes, route_loads


#We can also do this in parallel with other vehicles.

def PNN_solve(Dmat, order_sizes, capacity, fleetsize):
    """CVRP solve using PNN heuristic"""
    if sum(order_sizes) > fleetsize*capacity:
        return 'Insufficient fleet'
    # Initialise the routes
    routes = {i: [0] for i in range(fleetsize)}
    route_loads = {i: 0 for i in range(fleetsize)}
    
    # Start from depot (0) and we shall add in vertices
    N = len(Dmat)  # Number of customers + depot
    unvisited = list(range(1, N))  # Customers to visit
    while unvisited:
        nearerst_customer = None
        nearest_distance = float('inf')
        nearest_route = None
        for routeindex in range(fleetsize):
            current_location = routes[routeindex][-1]
            #Then we look through the unvisited nodes to find the nearest.
            for customer in unvisited:
                if Dmat[current_location][customer] < nearest_distance and route_loads[routeindex] + order_sizes[customer] <= capacity:
                    nearest_distance = Dmat[current_location][customer]
                    nearest_customer = customer
                    nearest_route = routeindex
        if nearest_customer is not None:
            # Add the nearest customer to the route
            routes[nearest_route].append(nearest_customer)
            route_loads[nearest_route] += order_sizes[nearest_customer]
            unvisited.remove(nearest_customer)
            #Three opt at each change. Hmm problem as depot has been changed here! UH-OH.
            # routes[nearest_route] = ih.three_opt(routes[nearest_route], Dmat)
        else:
            return 'Insufficient fleet (or infeasible method)' # again due to greedyness this could happen
    #We then return all routes to the depot
    for routeindex in range(fleetsize):
        routes[routeindex].append(0)  # Return to depot
    #Again could do some improvement algos here, yet to implement. 
    return routes, route_loads


#HMMM the issue with these is that they could travel very far away from the depot - the return distance is not accounted for. 
#This will be fixed in the insertion methods that we'll look at in a moment - but again this isnt great. We could allow routes to 
#grow in both directions. But you encounter the same issue with the endpoints. 
#I suppose this is why nearest neighbour in this way isnt very good. Another method could be to do a weighted average of distance #
#from the depot and the current location (ensuring we kinda have more 'circular' routes)
#Many drawbacks to NN - so is life - can investigate this further perhap.


#However - NN algos are decent for initialisation for improvement heuristics.

#Next look at insertion methods - like NN but more sophisticated as we needn't add at the end of the route. 
#Again will implemene sequential and parallel methods!


#Sequential insertion methods

def SInsert_solve(Dmat, order_sizes, capacity, fleetsize):
    """CVRP solve using sequential insertion heuristic"""
    if sum(order_sizes) > fleetsize*capacity:
        return 'Insufficient fleet'
    # Initialise the routes, note the depot is at the start and the end of the route.
    routes = {i: [0,0] for i in range(fleetsize)}
    route_loads = {i: 0 for i in range(fleetsize)}
    
    # Start from depot (0) and we shall add in vertices
    N = len(Dmat)  # Number of customers + depot
    unvisited = list(range(1, N))  # Customers to visit
    # Start with the first vehicle
    for vehicle in range(fleetsize):
        #We've already got the deopt in the route at the start and the end (hence two zeros)
        while unvisited and route_loads[vehicle] < capacity:
            # Find the nearest customer to the depot
            best_customer = None
            best_change = float('inf')
            for customer in unvisited:
                #Loop through the paths in the route to see where we should best insert!
                for i in range(len(routes[vehicle]) - 1):
                    change = Dmat[routes[vehicle][i]][customer] + Dmat[customer][routes[vehicle][i + 1]] - Dmat[routes[vehicle][i]][routes[vehicle][i + 1]]
                    if change < best_change and route_loads[vehicle] + order_sizes[customer] <= capacity:
                        best_change = change
                        best_customer = customer
                        best_position = i + 1
            if best_customer is not None:
                # Insert the best customer into the route
                routes[vehicle].insert(best_position, best_customer)
                route_loads[vehicle] += order_sizes[best_customer]
                unvisited.remove(best_customer)
            else:
                return 'Method problem!' #Again - greedyness doesn't garuntee a solution!
    return routes, route_loads


# We could try and spruce our insertion methods up - for example we could initialise a route with the furthest customer from the depot!


# Since sequential and parallel methods follow the same pattern - we should perhpas define a funciton implementing 
# them and just change criterion?- Indeed I'm copying and pasting a decent bit of code here. 





#Now lets do this in parallel
#Note - again, one can edit this so its not so greedy - take the node with maximal min diatance from routes - makes shape nicer.
# There are many tweaks that can be made to this method - farthest insert and regret insert.

def PInsert_solve(Dmat, order_sizes, capacity, fleetsize):
    """CVRP solve using parallel insertion heuristic"""
    if sum(order_sizes) > fleetsize*capacity:
        return 'Insufficient fleet'
    # Initialise the routes
    routes = {i: [0,0] for i in range(fleetsize)}
    route_loads = {i: 0 for i in range(fleetsize)}
    
    # Start from depot (0) and we shall add in vertices
    N = len(Dmat)  # Number of customers + depot
    unvisited = list(range(1, N))  # Customers to visit
    while unvisited:
        best_customer = None
        best_change = float('inf')
        best_route = None
        best_position = None
        for customer in unvisited:
            # Loop through the routes to find the best insertion point
            for vehicle in range(fleetsize):
                for i in range(len(routes[vehicle]) - 1):
                    change = Dmat[routes[vehicle][i]][customer] + Dmat[customer][routes[vehicle][i + 1]] - Dmat[routes[vehicle][i]][routes[vehicle][i + 1]]
                    if change < best_change and route_loads[vehicle] + order_sizes[customer] <= capacity:
                        best_change = change
                        best_customer = customer
                        best_route = vehicle
                        best_position = i + 1
        if best_customer is not None:
            # Insert the best customer into the route
            routes[best_route].insert(best_position, best_customer)
            route_loads[best_route] += order_sizes[best_customer]
            unvisited.remove(best_customer)
        else:
            return 'Method problem!' #Again - greedyness doesn't garuntee a solution!
    return routes, route_loads




#Next we look as savings heursitcs Clark Wright (CW) is the most well known. Again there are sequential and parallel methods.
#In general this has fleetsize are a decision variable.
#  
def CW_solve(Dmat, order_sizes, capacity):
    """Solves CVRP using Clarke-Wright Savings Heuristic."""
    num_customers = len(Dmat) - 1  # Exclude depot (index 0)

    # Compute Savings at start - this saves time!
    savings = []
    for i in range(1, num_customers + 1):
        for j in range(i + 1, num_customers + 1):
            save = Dmat[0][i] + Dmat[0][j] - Dmat[i][j]
            savings.append((save, i, j))
    savings.sort(reverse=True)  # Sort by descending savings - python uses 'timsort' O(nlog(n))

    # Okay we then create a route for each customer
    routes = {i: [i] for i in range(1, num_customers + 1)}
    route_loads = {i: order_sizes[i] for i in range(1, num_customers + 1)}
    #and merge these based on the savings. 
    for save, i, j in savings:
        if i in routes and j in routes and i != j:
            if route_loads[i] + route_loads[j] <= capacity:
                # Merge routes
                routes[i].extend(routes[j])
                route_loads[i] += route_loads[j]
                del routes[j]

    #  convert the routes to include depot (0)


    
    final_routes = [[0] + route + [0] for route in routes.values()]
    return {i: final_routes[i] for i in range(len(final_routes))}, route_loads

#The sequential method does one route at a time - we shant impelment here.

#Next we do a sweep method. Need to also look at methods implementing seeds, and cluster methods!

#Sweep is quite intuitive - we need to first select a 'random' vertex to take angles from. We'll just use the frist non-depot vertex.
#We'll implement as a cluster method - we cluster 'equally' (can be based on number of orders, or capactiy) into F clust
# ers. Then solve the TSP (eg. using NN above, or insert.)
#Also, we shall use equal-ish numbers in each cluster - this is sometimes more ideal for real world problems. 


#Here we sweep around and reorder the vertices in anticlockwise.
def sweep_order(coords : tuple , vertex_from=1):
    #Again, the depot is at zero - so we dont include this. 
    depot_coords = coords[0]
    remaining_coords = [ (x[0]- depot_coords[0], x[1]-depot_coords[1])  for x in coords[1:]]
    reordered_locations = [0,vertex_from]



    vec1 = remaining_coords[vertex_from] / np.sqrt(sum(np.square(remaining_coords[vertex_from])))
    #Then find orthogonal vector to this. 

    for i in range(len(remaining_coords)):
        if i != vertex_from:
            #Note that our coordinates are on a sphere (the globe) so this is a bit iffy. But since we're only dealing with the manchester area,
            #  we can treat this as a plane. 
            #can take dot prod then find the 
            dotprod = np.dot(vec1, remaining_coords[i]) 
            angle = np.arccos(dotprod/np.sqrt(sum(np.square(remaining_coords[i]))))
            #Next we find where this goes. But note we also

        