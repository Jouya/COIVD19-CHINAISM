import os
import csv
import networkx as nx
import random
airport_province = {"ANHUI": ["AQG", "JUH", "FUG", "HFE", "TXN"], "BEIJING": ["PEK", "PKX"],
                       "CHONGQING": ["CKG", "JIQ", "WXN","WSK"], "FUJIAN":["FOC","LCX", "SQJ", "JJN","WUS","XMN"],
                       "GANSU": ["DNH", "JGN","JIC","LHW","LNL","IQN","THQ","GXH","YZY"], "GUANGDONG": ["FUO", "CAN", "HUZ", "MXZ", "SWA", "SZX", "ZHA","ZUH"],
                       "GUANGXI": ["AEB", "BHY", "KWL","HCJ", "LZH", "NNG", "WUZ"],
                       "GUIZHOU": ["AVA", "BFJ", "KWE", "KJH", "LLB", "HZH", "LPF", "TEN", "ACX", "ZYI", "WMT"],
                       "HAINAN": ["HAK", "BAR", "SYX", "XYI"], "HEBEI": ["CDE", "HDG", "BPE", "SJW", "TVS", "ZQZ"],
                       "HEILONGJIANG": ["DQA", "FYJ", "HRB", "HEK", "JGD", "JMU", "JSJ", "JXA", "OHE", "MDG","NDG", "DTU", "LDS"],
                       "HENAN": ["LYA", "NNY", "XAI", "CGO"], "HONG KNOG": ["HKG"],
                       "HUBEI": ["ENH", "HPG", "WDS", "WUH", "XFN", "YIH"],
                       "HUNAN": ["CGD", "CSX", "HNY", "HJJ", "WGN", "LLF", "YYA", "DYG"],
                       "INNER MONGOLIA": ["AXF", "RHT", "YIE", "BAV", "RLK", "CIF", "EJN","ERL", "HLD", "HET", "HUO", "NZH", "XRQ", "DSN", "TGO", "HLH", "UCB", "WUA", "XIL", "NZL"],
                       "JIANGSU" : ["CZX", "HIA", "LYG", "NKG", "NTG", "WUX", "XUZ", "YNZ", "YTY"],
                       "JIANGXI": ["KOW", "JGS", "JDZ", "KHN", "SQD", "YIC"],
                       "JILIN": ["DBC", "NBS", "CGQ", "YSQ", "TNH", "YNJ"],
                       "LIAONING": ["AOG", "CNI", "CHG", "DLC", "DDG", "JNZ", "SHE", "YKH"],
                       "MACAU": ["MFM"], "NINGXIA" : ["GYU", "INC", "ZHY"],
                       "QINGHAI" : ["HXD", "GOQ", "GMQ", "HTT", "HBQ", "XNN", "YUS"],
                       "SHAANXI": ["AKA", "HZG", "XIY", "ENY", "UYN"],
                       "SHANDONG" : ["DOY", "TNA", "JNG", "LYI", "TAO", "RIZ", "WEF", "WEH", "YNT"],
                       "SHANGHAI": ["SHA", "PVG"], "SHANXI": ["CIH", "DAT", "LGQ", "LLV", "TYN", "WUT", "YCU"],
                       "SICHUAN" : ["BZX", "CTU", "DCY", "DAX", "GZG", "GYS", "AHJ", "JHZ", "LZO", "MIG", "NAO", "PZI", "XIC", "YBP"],
                       "TIANJIN" : ["TSN"], "XIZANG": ["LXA", "LYZ", "BPX", "PKZ", "NGQ"],
                       "XINJIANG": ["AKU", "AAT", "BPL", "KJL", "FYN", "HMI", "HTN", "KRL", "KCA", "KRY", "KHG", "IQM", "RQA", "SHF", "TCG", "TWC", "TLQ", "URC", "NLT", "QSZ", "YIN"],
                       "YUNNAN" : ["BSD", "CWJ", "DLU", "JHG", "KMG", "JMJ", "LJG", "LUM", "NLH", "SYM", "DIG", "TCZ", "WNH", "ZAT"],
                       "ZHEJIANG" : ["HGH", "NGB", "JUZ", "HYN", "WNZ", "YIW", "HSN"]}
COMMUNITY_SIZE = 153
NUM_NEW_EDGES = 153
K_NEAREST_NEIGHBORS = 7
REWIRING_PROBABILITY = 0.5
PATHOGEN_TRANSMISSION = 0.7
DEATH_PROBABLITY = 0.2
def extract_info (r=0):
    f = open(r"C:\Users\jooya\OneDrive\Desktop\College\Spring 2020\Contagion\Project\airports.txt", "r")
    lines = f.readlines()
    city_airport = []
    airport_city = {}
    # cities and their airport codes
    for line in lines:
        items = line.strip().split("\t")
        city = items[0]
        airport = (items[1].split()[-1].strip("(").strip(")"))
        city_airport.append((city,airport))
        airport_city[airport] = city
    
    # population data for each chinese city
    city_population = {}
    f3 = open(r"C:\Users\jooya\OneDrive\Desktop\College\Spring 2020\Contagion\Project\Population.txt", "r")
    data = f3.readlines()
    for line in data:
        data = line.split(",")
        if data[4].strip() == '\"China\"':
            city_population[data[0].strip("\"")] = data[9]

    # population data for the chinese that we have air-traffic data for
    final_data = {}
    for item in city_airport:
        if item[0] in city_population.keys():
            final_data[item[0]] = (item[1],city_population[item[0]])

    if (r == 1):
        return final_data, city_airport, city_population
    else:
        return final_data, airport_city

def create_network_local():
    # We also implement the SEIR Model structure here
    community = nx.watts_strogatz_graph(COMMUNITY_SIZE,K_NEAREST_NEIGHBORS, REWIRING_PROBABILITY)
    for j in range(len(community.nodes)):
        community.nodes[j]["Susceptible"] = True
        community.nodes[j]["Exposed"] = False
        community.nodes[j]["Infected"] = False
        community.nodes[j]["Recovered"] = False
        community.nodes[j]["Deceased"] = False
        community.nodes[j]["Incubation Period"] = random.randint(1,7)
        community.nodes[j]["Infectious Period"] = random.randint(1,7)

    return community

def start_simulation(city_name, city_data, airport_volumes, airport_city, luckdown_time, duration):
    # number of communites/nodes in the city
    num_communites = int(int(city_data[city_name][1].strip("\""))/COMMUNITY_SIZE)
    city = nx.barabasi_albert_graph(num_communites, NUM_NEW_EDGES)
    infected_cities = {}
    infected_cities[city_name] = [city]

    # randomly pick a community to infect
    rand_community = random.randint(0,len(infected_cities[city_name][0].nodes)-1)
    # create a local community
    infected_cities[city_name][0].nodes[rand_community]["Community"] = create_network_local()
    # Within that community, infect a random person
    patient_zero = random.randint(0,144)
    infected_cities[city_name][0].nodes[rand_community]["Community"].nodes[patient_zero]["Infected"] = True

    exposed_infected_communites = {}
    exposed_infected_communites[rand_community] = [[patient_zero],[]]
    infected_cities[city_name].append(exposed_infected_communites)
    infected_cities[city_name] += [1,0,0]

    # INFECTED_CITIES STRUCTURE:
    # INFECTED_CITIES[name of the city] = (graph of the city, a dictionary containing infected communites as keys and infected nodes in the [0] index and exposed nodes in [1])

    max_infected = 1
    max_recovered = 0
    max_dead = 0
    luckdown = False
    social_distancing = 0.0
    for i in range(0,duration):
        if i == luckdown_time:
            luckdown = True
            social_distancing = round(PATHOGEN_TRANSMISSION/2)
        # the infection begins to spread
        for city in list(infected_cities.keys()):
            for community in infected_cities[city][1].keys():
                # community_level transmission, look at every infected node within the current community
                for infected in infected_cities[city][1][community][0]:
                    # expose neigbors
                    for adj in infected_cities[city][0].nodes[community]["Community"].adj[infected]:
                        # only expose the neigbor if they aren't already exposed or have been before
                        if (adj not in infected_cities[city][1][community][1]) and (infected_cities[city][0].nodes[community]["Community"].nodes[adj]["Susceptible"] == True):
                            if random.random() <= PATHOGEN_TRANSMISSION - social_distancing:
                                #This will ensure that node will never get exposed/infected again
                                infected_cities[city][0].nodes[community]["Community"].nodes[adj]["Susceptible"] = False
                                infected_cities[city][0].nodes[community]["Community"].nodes[adj]["Exposed"] = True
                                # add the node to exposed list 
                                infected_cities[city][1][community][1].append(adj)
                    # ***RECOVERY***
                    # They node is done being infectious, they will now either die or recover
                    if (infected_cities[city][0].nodes[community]["Community"].nodes[infected]["Infectious Period"] - 1 == 0):
                        # remove the node from the infected nodes list
                        infected_cities[city][1][community][0].remove(infected)
                        infected_cities[city][0].nodes[community]["Community"].nodes[infected]["Infected"] = False
                        # roll the dice
                        if (random.random() >= DEATH_PROBABLITY):
                            infected_cities[city][0].nodes[community]["Community"].nodes[infected]["Recovered"] = True
                            infected_cities[city][3] += 1
                            max_recovered += 1
                        else:
                            infected_cities[city][0].nodes[community]["Community"].nodes[infected]["Deceased"] = True
                            infected_cities[city][4] += 1
                            max_dead += 1
                    # decrease their infectious period 
                    else:
                        infected_cities[city][0].nodes[community]["Community"].nodes[infected]["Infectious Period"] -= 1
                for exposed in infected_cities[city][1][community][1]:
                    # They node is done being exposed, they will now be infectious
                    if (infected_cities[city][0].nodes[community]["Community"].nodes[exposed]["Incubation Period"] - 1 == 0):
                        infected_cities[city][1][community][0].append(exposed)
                        infected_cities[city][0].nodes[community]["Community"].nodes[exposed]["Infected"] = True
                        infected_cities[city][2] += 1
                        max_infected += 1
                        # remove from exposed nodes list
                        infected_cities[city][1][community][1].remove(exposed)
                        infected_cities[city][0].nodes[community]["Community"].nodes[exposed]["Exposed"] = False
                    else:
                        infected_cities[city][0].nodes[community]["Community"].nodes[exposed]["Incubation Period"] -= 1

            # city-level transmission
            for community_adj in infected_cities[city][0].adj[community]:
                # the neighboring community is already infected, ignore it
                if community_adj not in infected_cities[city][1].keys():
                    # the higher the number of infected people in one community, the more likely it is for to spread to another community
                    if random.random() <= ((PATHOGEN_TRANSMISSION - social_distancing) *((len(infected_cities[city][1][community][0])))/COMMUNITY_SIZE):
                        # create a a new community and then randomly infect a person within the newly infected community
                        infected_cities[city][0].nodes[community_adj]["Community"] = create_network_local()
                        patient_zero = random.randint(0,144)
                        infected_cities[city][0].nodes[community_adj]["Community"].nodes[patient_zero]["Susceptible"] = False
                        infected_cities[city][0].nodes[community_adj]["Community"].nodes[patient_zero]["Exposed"] = True
                        infected_cities[city][1][community_adj] = [[],[patient_zero]]

            if (not luckdown):
                for destination in airport_volumes[city_data[city_name][0]]:
                    #print(((infected_cities[city][2] - (infected_cities[city][4] + infected_cities[city][3]))/int(city_data[city_name][1].strip("\""))) * airport_volumes[city_data[city_name][0]][destination] * 10 )
                    # you can't infect the same city twice
                    if (airport_city[destination] not in infected_cities.keys()):
                        # roll the dice, see if the pathegon is transmitted via the the airport route
                        if (random.random() <= ((PATHOGEN_TRANSMISSION - social_distancing) * ((infected_cities[city][2] - (infected_cities[city][4] + infected_cities[city][3]))/int(city_data[city_name][1].strip("\""))) * airport_volumes[city_data[city_name][0]][destination])):
                            # infect another city
                            # number of communites/nodes in the city
                            new_city_name = airport_city[destination]
                            new_num_communites = int(int(city_data[new_city_name][1].strip("\""))/COMMUNITY_SIZE)
                            new_city = nx.barabasi_albert_graph(new_num_communites, NUM_NEW_EDGES)
                            infected_cities[new_city_name] = [new_city]
                            # randomly pick a community to infect
                            new_rand_community = random.randint(0,len(infected_cities[new_city_name][0].nodes)-1)
                            # create a local community
                            infected_cities[new_city_name][0].nodes[new_rand_community]["Community"] = create_network_local()
                            # Within that community, infect a random person
                            new_patient_zero = random.randint(0,144)
                            infected_cities[new_city_name][0].nodes[new_rand_community]["Community"].nodes[new_patient_zero]["Infected"] = True

                            new_exposed_infected_communites = {}
                            new_exposed_infected_communites[new_rand_community] = [[new_patient_zero],[]]
                            infected_cities[new_city_name].append(new_exposed_infected_communites)
                            infected_cities[new_city_name] += [1,0,0]


    print("Number of cities infected (spread):", len(infected_cities.keys()))
    print("Total number of Infected: ", max_infected)
    print("Total number of Deaths: ", max_dead)
    print("Total number of Recovery: ", max_recovered)

def plane_volumes():
    '''None --> list, dict
    
    Uses air_traffic.txt to first create a list of all airports in China from the
    airport_province dictionary. Then creates a dictionary with plane models as keys
    and average plane volumes as values.'''
    
    all_airports = [] #A list of all Chinese airports
    
    for province_group in airport_province.values():
        for airport_code in province_group:
            all_airports.append(airport_code)
            
    
    observed_planes = [] #A list of planes as they are observed in air_traffic.txt (some routes list mutliple planes)
    
    f = open(r"C:\Users\jooya\OneDrive\Desktop\College\Spring 2020\Contagion\Project\air_traffic.txt", "r")
    air_data = f.readlines()
    for line in air_data:
        items = line.strip().split(",")
        # add the plane(s)
        if items[2] in all_airports and items[4] in all_airports and items[-1] not in observed_planes:
            observed_planes.append(items[-1])
    
    
    all_planes = []  #A list of every plane used in any domestic route. Primarily used to create volume dictionary
    
    for group in observed_planes:
        line = group.strip().split(" ")
        for plane_code in line:
            if plane_code not in all_planes:
                all_planes.append(plane_code)
    
    indiv_plane_volumes = {"321": 220, "320": 150, "319": 160, "330": 278, "738": 162, "737": 174, "YN7": 17,
               "CR7": 78, "333": 262, "340": 250, "CR2": 50, "772": 368, "733": 143, "777":368, "73G": 143,
               "E90": 100, "332": 250, "77W": 264, "752": 200, "CR9": 90, "ERJ": 87, "787": 184,
               "32S": 150, "343": 247, "EMB": 21, "767": 216, "739": 178, "773": 264, "744": 400,
               "380": 544, "AB6": 250, "757": 200, "346": 370, "747": 366, "CRJ": 70}
    
    #Using 'all_planes' above, I manually found the passenger volume ofe each plane in the list and
    # created the dictionary 'indiv_plane_volumes', where the plane model serve as keys and the
    # passenger values as respective values.
    
    #As I noted before, there are multiple planes that fly some of the air routes. To this regard,
    # I have decided that the number of passengers that fly these routes is the average passenger
    # volume of these planes.
    
    plane_groups_by_volume = {}
    
    for group in observed_planes:
        volume = 0
        line = group.strip().split(" ")
        for code in line:
            volume += indiv_plane_volumes.get(code)
            plane_groups_by_volume[group] = round(volume/len(line))
            
    return all_airports, plane_groups_by_volume
    

def route_volumes(city_data, airport_city):
    '''None --> Dict
    
    Creates a dictionary where the departing airports are keys, and dictionaries
    are values. In the nested dictionaries, the destination airports are the keys,
    the volumes of passengers arriving at the destination airport from the departing
    airport are the values.'''
    
    chinese_airports, volume = plane_volumes()

    routes_by_volume = []
    
    f = open(r"C:\Users\jooya\OneDrive\Desktop\College\Spring 2020\Contagion\Project\air_traffic.txt", "r")
    routes = f.readlines()
    for route in routes:
        splited_route = route.strip().split(",")
        if splited_route[2] in chinese_airports and splited_route[4] in chinese_airports:
            routes_by_volume.append([splited_route[2], splited_route[4], volume.get(splited_route[-1])])
    
    yeaboi = {}
    
    
    for airport in chinese_airports:
        if (airport in airport_city.keys() and airport_city[airport] in city_data.keys()):
            inside = {}
            for route in routes_by_volume:
                if route[0] == airport and route[1] in airport_city.keys() and airport_city[route[1]] in city_data.keys():
                    inside[route[1]] = route[2]
            yeaboi[airport] = inside
    return yeaboi
            
    
def main():
    final_data, airport_city = extract_info()
    # start simulation-- start from Wuhan
    for j in range(0,10):
        start_simulation("Wuhan", final_data, route_volumes(final_data, airport_city), airport_city, 45, 135)

    # TO DO:
    # 1. Visualization

   
main()