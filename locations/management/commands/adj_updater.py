import os
import math as m


class UpdateAdjList:
    def __init__(self):
        self.adj_list = self.load_adj_list()
        self.adj_list_path = f"{os.getcwd()}/locations/management/commands/adj_list.py"

    def load_adj_list(self):
        adj_list_path = f"{os.getcwd()}/locations/management/commands/adj_list.py"
        adj_list = {}

        with open(adj_list_path, "r") as f:
            adj_list = dict(eval(f.read()))

        return adj_list

    @staticmethod
    def get_location_name(location):
        name = location.name

        if "Node" in name:
            return int(name.replace("Node", ""))
        return name

    @staticmethod
    def calculate_distance(loc1, loc2):
        x_loc1 = loc1.pixel_x if loc1.pixel_x else 0
        y_loc1 = loc1.pixel_y if loc1.pixel_y else 0
        x_loc2 = loc2.pixel_x if loc2.pixel_x else 0
        y_loc2 = loc2.pixel_y if loc2.pixel_y else 0

        return m.sqrt(0.001 * ((x_loc1 - x_loc2) ** 2 + (y_loc1 - y_loc2) ** 2))

    """
    This function updates the adj_list with the new connections and distances betweem them.
    """

    def add_conns(self, loc1, connections=[]):
        new_data = self.adj_list.copy()
        for loc2 in connections:
            if loc2:
                distance = UpdateAdjList.calculate_distance(loc1, loc2)
                loc1_name = UpdateAdjList.get_location_name(loc1)
                loc2_name = UpdateAdjList.get_location_name(loc2)
                try:
                    new_data[loc1_name]
                except KeyError:
                    new_data[loc1_name] = {}
                try:
                    new_data[loc2_name]
                except KeyError:
                    new_data[loc2_name] = {}
                new_data[loc1_name][loc2_name] = distance
                new_data[loc2_name][loc1_name] = distance

                with open(self.adj_list_path, "w") as f:
                    f.write(str(new_data))

    def delete_all_connections(self, location):
        new_data = self.adj_list.copy()
        loc_name = UpdateAdjList.get_location_name(location)

        if loc_name in new_data:
            new_data.pop(loc_name)
            for key in new_data:
                if loc_name in new_data[key]:
                    new_data[key].pop(loc_name)

        with open(self.adj_list_path, "w") as f:
            f.write(str(new_data))

    def delete_connections(self, location, connections):
        new_data = self.adj_list.copy()
        loc1_name = self.get_location_name(location)

        for loc2 in connections:
            loc2_name = self.get_location_name(loc2)

            if loc2_name in new_data:
                if loc1_name in new_data[loc2_name]:
                    new_data[loc2_name].pop(loc1_name)
            if loc1_name in new_data:
                if loc2_name in new_data[loc1_name]:
                    new_data[loc1_name].pop(loc2_name)

        with open(self.adj_list_path, "w") as f:
            f.write(str(new_data))
