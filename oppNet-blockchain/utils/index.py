import math
from storage import fetch_latest_info, fetch_distance 
def check_reachability(station1, station2, net, timeout=15):
    # Check if stations are in each other's coverage range and can reach each other
    distances_output = net.pingFull([net.get(station1), net.get(station2)], timeout)
    
    # Fetch station information from Mininet's station properties
    sta1 = net.get(station1)
    sta2 = net.get(station2)

    # Check if the interface of station 2 is up
    if not sta2.intf().isUp():
        return False

    # Calculate the distance between the stations
    distance = calculate_distance(sta1, sta2)
    return sta1.wintfs[0].range >= distance

def get_station_number(station_name):
    # Extract the numeric part from the station name
    return int(''.join(filter(str.isdigit, station_name)))

def get_key(station1, station2):
    # Get the numeric part from the station names
    number1 = get_station_number(station1)
    number2 = get_station_number(station2)

    # Ensure that the station with the lower number comes first
    return ("sta" + str(number1), "sta" + str(number2)) if number1 < number2 else ("sta" + str(number2), "sta" + str(number1))

def check_reachability_with_smart_contract(station1, station2, latest_info, distances):
    # Extract station information from the latest_info dictionary
    sta1_info = latest_info.get(station1, {}).get('network_info', {})
    sta2_info = latest_info.get(station2, {}).get('network_info', {})

    # Check if the 'range' key is present in the station information
    if 'range' not in sta1_info or 'range' not in sta2_info:
        print(f"Error: 'range' key not found in station information for {station1} or {station2}")
        return False

    # Compare the range of station1 with the distance in the distances dictionary
    return float(sta1_info['range']) >= distances[get_key(station1, station2)] and sta2_info['status'] == "online"

def check_node_status_with_smart_contract(station, latest_info):
    station_info = latest_info.get(station, {}).get('network_info', {})
    
    if 'status' in station_info:
        return station_info['status']
    else:
        print(f"Error: 'status' key not found in station information for {station}")
        return None

def check_node_status_without_smart_contract(station, net):
    for sta in net.stations:
        if sta.name == station:
            sta_info = sta

    sta = net.get(sta_info.name)


    if not sta.intf().isUp():
        return "online"
    return "offline"


def calculate_distance(sta1, sta2):
    pos1 = sta1.position
    pos2 = sta2.position
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance

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

# def find_route_with_smart_contract(net, sta_start, sta_end):
#     # Fetch distances from the smart contract
#     distances, latest_infor = fetch_contract_storage()

#     # Convert distances from strings to floats
#     for edge, distance_str in distances.items():
#         distances[edge] = float(distance_str)

#     # Implement flooding method to find the route
#     visited = set()
#     queue = [[sta_start]]

#     while queue:
#         path = queue.pop(0)
#         node = path[-1]

#         if node == sta_end:
#             return path, distances[sta_start][sta_end]

#         if node not in visited:
#             # Check reachability from the current station to every other station
#             neighbors = []
#             for other_sta in net.stations:
#                 if other_sta.name != node and other_sta.name not in path:
#                     if check_reachability_with_smart_contract(node, other_sta.name, latest_infor, distances):
#                         neighbors.append(other_sta.name)

#             if neighbors:   
#                 # Sort neighbors by distance (you can use a more sophisticated metric)
#                 sorted_neighbors = sorted(neighbors, key=lambda neighbor: distances[get_key(node, neighbor)])
#                 # Add the neighbor with the shortest path to the queue
#                 new_path = list(path)
#                 new_path.append(sorted_neighbors[0])
#                 queue.append(new_path)

#             visited.add(node)

#     print(f"No route found between {sta_start} and {sta_end}")
#     return None, None

