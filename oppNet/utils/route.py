def find_route_without_smart_contract(net, sta_start, sta_end):
    # Fetch station information from Mininet's station properties
    for sta in net.stations:
        if sta.name == sta_start:
            sta_start_info = sta
        if sta.name == sta_end:
            sta_end_info = sta

    pos_sta_start = sta_start_info.position
    range_sta_start = sta_start_info.wintfs[0].range

    pos_sta_end = sta_end_info.position
    range_sta_end = sta_end_info.wintfs[0].range

    # Implement flooding method to find the route
    visited = set()
    queue = [[sta_start_info.name]]

    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node == sta_end_info.name:
            print(path, calculate_distance(sta_start_info, sta_end_info))
            return path, calculate_distance(sta_start_info, sta_end_info)

        if node not in visited:
            # Check reachability from the current station to every other station
            neighbors = []
            for other_sta in net.stations:
                if other_sta.name != node and other_sta.name not in path:
                    if check_reachability(node, other_sta.name, net):
                        neighbors.append(other_sta.name)

            if neighbors:
                # Sort neighbors by distance (you can use a more sophisticated metric)
                sorted_neighbors = sorted(neighbors, key=lambda neighbor: calculate_distance(sta_start_info, net.get(neighbor)))
                # Add the neighbor with the shortest path to the queue
                new_path = list(path)
                new_path.append(sorted_neighbors[0])
                queue.append(new_path)

            visited.add(node)

    print(f"No route found between {sta_start_info.name} and {sta_end_info.name}")
    return None, None

def find_route_with_smart_contract(net, sta_start, sta_end):
    # Fetch distances from the smart contract
    distances, latest_infor = fetch_contract_storage()

    # Convert distances from strings to floats
    for edge, distance_str in distances.items():
        distances[edge] = float(distance_str)

    # Implement flooding method to find the route
    visited = set()
    queue = [[sta_start]]

    while queue:
        path = queue.pop(0)
        node = path[-1]

        if node == sta_end:
            return path, distances[sta_start][sta_end]

        if node not in visited:
            # Check reachability from the current station to every other station
            neighbors = []
            for other_sta in net.stations:
                if other_sta.name != node and other_sta.name not in path:
                    if check_reachability_with_smart_contract(node, other_sta.name, latest_infor, distances):
                        neighbors.append(other_sta.name)

            if neighbors:   
                # Sort neighbors by distance (you can use a more sophisticated metric)
                sorted_neighbors = sorted(neighbors, key=lambda neighbor: distances[get_key(node, neighbor)])
                # Add the neighbor with the shortest path to the queue
                new_path = list(path)
                new_path.append(sorted_neighbors[0])
                queue.append(new_path)

            visited.add(node)

    print(f"No route found between {sta_start} and {sta_end}")
    return None, None

