#Here we prvide the implementation of the improvement heuristics Namely the lambda opt (Intra) and such and the inter-route improvements also!


import numpy as np
import pandas as pd 
import time

#First - we do some intra route improvements. 
#Recolation is the simplest. Just take a thang out and replace it somewhere else.
#Should invoke time lim
#Also, we're greedy and accept the first improvement (hence break break break)
def relocation_improve(route, Dmat,timelim = None):
    """Relocation improvement algorithm"""
    best = route[:]
    size = len(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, size - 1):
            for j in range(1, size - 1):
                if i == j:
                    continue 
            else: 
                A,B,C = best[i-1], best[i], best[i+1]
                D,E = best[j], best[j+1]

                distance_before = Dmat[A][B] + Dmat[B][C] + Dmat[D][E]
                distance_after = Dmat[A][C] + Dmat[D][B] + Dmat[B][E] 

                if distance_after < distance_before:
                    # Relocate B (i-th node) after D (j-th node)
                    node = best.pop(i)
                    # If i < j, index shifts left after pop
                    if i < j:
                        best.insert(j, node)
                    else:
                        #If i >= j, our pop requires a lil shift!
                        best.insert(j + 1, node)
                    improved = True
                    break
            if improved:
                break
        if improved:
            break
    return best


#Similarly can implement an exhange improvement algorithm - this isnt so greedy - searches for the best exchange. 
def exchange_improve(route,Dmat):
    """Exchange improvement algorithm"""
    best = route[:]
    size = len(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, size - 1):
            for j in range(i+1,size-1):
                if i ==j:
                    continue
                

                A,B,C = best[i-1], best[i], best[i+1]
                D,E,F = best[j-1], best[j], best[j+1]
                distance_before = Dmat[A][B] + Dmat[B][C] + Dmat[D][E] + Dmat[E][F]
                distance_after = Dmat[A][E] + Dmat[E][C] + Dmat[D][B] + Dmat[B][F]
                #Yep, then we check if there is improvement
                if distance_after < distance_before:
                    # Exchange B (i-th node) with D (j-th node)
                    best[i], best[j] = best[j], best[i]
                    improved = True
        route = best
    return best                    

#We shall only use two opt and three-opt - due to trade-off between time and quality.
#We'll stop once lambdda-opt optimality i reached.
#Currently this could violate our cap constraint - no it couldn't becasue the route is already feasible 
# - it could be a problem if we introduced pickpups also. 

#Also note that here we're using the best poss reconneciton - we could use first for speed (shall do in 3-opt)
#Also - we shouldn't be able to move the first and last node as these must remain as the start and end of the route.
def two_opt(route, Dmat):
    """2-opt method"""
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            # Symmetry means we can just look at nodes after i
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue  # skips adjacent nodes

                # Nodes before and after the segment
                A, B = best[i - 1], best[i]
                C, D = best[j], best[j + 1]

                # Current distance
                dist_before = Dmat[A][B] + Dmat[C][D]
                # Distance after reversing [i:j]
                dist_after = Dmat[A][C] + Dmat[B][D]

                # Check if the swap improves the tour
                if dist_after < dist_before:
                    best[i:j + 1] = best[i:j + 1][::-1]
                    improved = True
        route = best
    return best

# We now implement 3-opt - with first reconneciton.
#2 opt is a subset of three opt  - ie. when the reconnection permutation has a fixed point. 
#Cant include the end bits. 
def three_opt(route, Dmat):
    """3-opt with first reconneciton"""
    best = route[:]
    size = len(best)
    improved = True

    while improved:
        improved = False
        #I suppose we should check that the route isnt too small
        for i in range(1, size - 5):
            for j in range(i + 2, size - 3):
                for k in range(j + 2, size - 1):
                    # Original segments: (i-1,i), (j-1,j), (k-1,k)
                    A, B = best[i - 1], best[i]
                    C, D = best[j - 1], best[j]
                    E, F = best[k - 1], best[k]

                    d0 = Dmat[A][B] + Dmat[C][D] + Dmat[E][F]

                    # 7 possible reconnections (only showing 4 common ones below)
                    options = []

                    # 1. Reverse segment B-C
                    new1 = best[:i] + best[i:j][::-1] + best[j:k] + best[k:]
                    d1 = Dmat[A][best[j - 1]] + Dmat[best[i]][D] + Dmat[E][F]
                    options.append((d1, new1))

                    # 2. Reverse segment D-E
                    new2 = best[:i] + best[i:j] + best[j:k][::-1] + best[k:]
                    d2 = Dmat[A][B] + Dmat[C][best[k - 1]] + Dmat[best[j]][F]
                    options.append((d2, new2))

                    # 3. Reverse B-C and D-E
                    new3 = best[:i] + best[i:j][::-1] + best[j:k][::-1] + best[k:]
                    d3 = Dmat[A][best[j - 1]] + Dmat[best[i]][best[k - 1]] + Dmat[best[j]][F]
                    options.append((d3, new3))

                    # 4. Swap B-E and reverse mid
                    new4 = best[:i] + best[j:k] + best[i:j] + best[k:]
                    d4 = Dmat[A][D] + Dmat[E][B] + Dmat[C][F]
                    options.append((d4, new4))

                    # Evaluate
                    for new_dist, new_route in options:
                        if new_dist < d0:
                            best = new_route
                            improved = True
                            break  # Greedy: accept first improvement
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    return best


