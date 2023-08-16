import os
import math as m

"""
This function updates the adj_list with the new connections and distances betweem them.
"""
def add_conns(loc1, loc2):
    working_directory = os.getcwd()
    os.chdir(working_directory+ "/locations/management/commands/")
    with open("adj_list.py", 'r') as f:
        data = f.read()
        data = dict(eval(data))
        x_loc1 = loc1.pixel_x if loc1.pixel_x else 0
        y_loc1 = loc1.pixel_y if loc1.pixel_y else 0
        x_loc2 = loc2.pixel_x if loc2.pixel_x else 0
        y_loc2 = loc2.pixel_y if loc2.pixel_y else 0

        lld = m.sqrt(abs(0.001 * ((x_loc1-x_loc2)**2 + (y_loc1 - y_loc2)**2)))
        if "Node" in loc1.name:
            loc1 = int(loc1.name.replace("Node", ""))
        else:
            loc1 = loc1.name
        if "Node" in loc2.name:
            loc2 = int(loc2.name.replace("Node", ""))
        else:
            loc2 = loc2.name
        
        try: 
            data[loc1]
        except KeyError:
            data[loc1] = {}
        try:
            data[loc2]
        except KeyError:
            data[loc2] = {}
        data[loc1][loc2] = lld
        data[loc2][loc1] = lld
        data = str(data)
        
        with open("adj_list.py", 'w') as f:
            f.write(data)

    os.chdir(working_directory)

import os

def delete_connections(location):
    working_directory = os.getcwd()
    os.chdir(working_directory + "/locations/management/commands/")
    
    with open("adj_list.py", 'r') as f:
        data = f.read()
        data = dict(eval(data))
        name = location.name
        if "Node" in name:
            name = int(name.replace("Node", ""))
        else:
            name = name
        if name in data:
            data.pop(name)
            for key in data:
                if name in data[key]:
                    data[key].pop(name)
    
    with open("adj_list.py", 'w') as f:
        f.write(str(data))
    
    os.chdir(working_directory)
