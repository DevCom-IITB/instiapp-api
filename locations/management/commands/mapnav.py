from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
import sys
from locations.serializers import LocationSerializerMin
from locations.models import Location
import os
import math as m

# class ProfileFetcher():
#     """Helper to get dictionary of profiles efficiently."""
#     def __init__(self):
#         self.roll_nos = None

#     def get_roll(self):
#         if not self.roll_nos:
#             self.roll_nos = UserProfile.objects.filter(active=True).values_list('roll_no', flat=True)
#         return self.roll_nos


# profile_fetcher = ProfileFetcher()

"""
Returns adj_list with the distances and updates database for
Locations models to contain the node points(if they didn't).
"""


class handle_entry:
    def __init__(self):
        self.coordinates = [
            [2091, 747],
            [2189, 756],
            [2269, 765],
            [2332, 783],
            [2483, 729],
            [2430, 810],
            [2501, 854],
            [2554, 899],
            [2608, 934],
            [2634, 961],
            [2741, 916],
            [2875, 854],
            [2706, 1014],
            [2795, 1094],
            [2848, 1077],
            [3017, 1014],
            [2955, 952],
            [3124, 979],
            [3204, 952],
            [3266, 996],
            [3329, 1014],
            [3525, 1059],
            [3614, 1094],
            [3685, 1112],
            [3587, 1166],
            [3783, 1139],
            [3685, 1210],
            [3863, 1130],
            [3943, 1166],
            [3987, 1192],
            [4148, 1112],
            [4237, 1068],
            [4112, 1041],
            [3952, 988],
            [3898, 1246],
            [3845, 1264],
            [3783, 1228],
            [3649, 1370],
            [3836, 1424],
            [3934, 1442],
            [3863, 1531],
            [3845, 1557],
            [3881, 1557],
            [3952, 1575],
            [4014, 1593],
            [4050, 1602],
            [4130, 1620],
            [4148, 1593],
            [4192, 1637],
            [4165, 1700],
            [4094, 1780],
            [4148, 1771],
            [4059, 1798],
            [4014, 1860],
            [3916, 1967],
            [3872, 2011],
            [3747, 1958],
            [3836, 2065],
            [3792, 2118],
            [3703, 2207],
            [3622, 2296],
            [3587, 2350],
            [3631, 2394],
            [3631, 2447],
            [4023, 2590],
            [4076, 2528],
            [4112, 2474],
            [4050, 2456],
            [4201, 2261],
            [4281, 2145],
            [4352, 2145],
            [4344, 2100],
            [4201, 2065],
            [4148, 2047],
            [4157, 2020],
            [4219, 1949],
            [4272, 1860],
            [4317, 1807],
            [4468, 1842],
            [4557, 1735],
            [4619, 1646],
            [4593, 1575],
            [4513, 1611],
            [4406, 1593],
            [4361, 1557],
            [4228, 1522],
            [4290, 1433],
            [4361, 1433],
            [4148, 1504],
            [4094, 1495],
            [3979, 1379],
            [4032, 1308],
            [4059, 1255],
            [3970, 1290],
            [3916, 1290],
            [3329, 1531],
            [3266, 1486],
            [3151, 1397],
            [3071, 1326],
            [3124, 1308],
            [3195, 1264],
            [3008, 1272],
            [2875, 1166],
            [2652, 1228],
            [2608, 1272],
            [2599, 1326],
            [2715, 1522],
            [2723, 1575],
            [2706, 1620],
            [2652, 1646],
            [2545, 1682],
            [2528, 1726],
            [2421, 1691],
            [2314, 1691],
            [2109, 1718],
            [2563, 1744],
            [2625, 1726],
            [2670, 1726],
            [2706, 1735],
            [2839, 1798],
            [2857, 1824],
            [2848, 1860],
            [2821, 1878],
            [2430, 2216],
            [2412, 2269],
            [2367, 2403],
            [2243, 2474],
            [1815, 2715],
            [1646, 2777],
            [1531, 2795],
            [1762, 2893],
            [1798, 2919],
            [1878, 3026],
            [2172, 2937],
            [2189, 2893],
            [2376, 2581],
            [2608, 2376],
            [2590, 2305],
            [2554, 2287],
            [2697, 2154],
            [2750, 2154],
            [2893, 2207],
            [3053, 2056],
            [3142, 1967],
            [3275, 1842],
            [3302, 1842],
            [3293, 1798],
            [3124, 1753],
            [3142, 1691],
            [3213, 1682],
            [3293, 1655],
            [3355, 1673],
            [3364, 1718],
            [2421, 2901],
            [2554, 2652],
            [2759, 2456],
            [2928, 2314],
            [2982, 2261],
            [3017, 2225],
            [3382, 2367],
            [3444, 2376],
            [3507, 2341],
            [3160, 2100],
            [3240, 2011],
            [3302, 1967],
            [3364, 1904],
            [3382, 1869],
            [3400, 1815],
            [3427, 1691],
            [3418, 1629],
            [3516, 1682],
            [3329, 2234],
            [3409, 2136],
            [3489, 2038],
            [3551, 1967],
            [3587, 1931],
            [3649, 1860],
            [3703, 1815],
            [3783, 1718],
            [3667, 1673],
            [3845, 1629],
            [3934, 2723],
            [3898, 2777],
            [3845, 2857],
            [3800, 2919],
            [4655, 1513],
            [4780, 1370],
            [4860, 1272],
            [4726, 1086],
            [4593, 943],
            [4548, 934],
            [4495, 943],
            [4335, 1005],
            [1361, 2732],
            [1201, 2652],
            [1121, 2652],
            [925, 2572],
            [756, 2501],
            [721, 2394],
            [649, 2367],
            [1041, 2625],
            [4780, 1370],
            [4691, 1335],
            [4611, 1317],
            [4566, 1308],
            [4513, 1290],
            [4459, 1281],
            [4397, 1272],
            [4352, 1255],
            [4281, 1228],
            [4210, 1246],
            [4094, 1237],
            [4032, 1272],
            [3970, 1299],
            [3863, 1272],
            [4726, 1290],
            [4762, 1255],
            [4726, 1219],
            [4700, 1183],
            [4673, 1157],
            [4628, 1219],
            [4566, 1166],
            [4539, 1210],
            [4513, 1210],
            [4477, 1255],
            [4851, 1290],
            [4851, 1246],
            [4806, 1192],
            [4771, 1148],
            [4878, 1130],
            [4700, 1130],
            [4717, 1086],
            [4673, 1050],
            [4530, 1059],
            [4450, 1086],
            [4388, 1148],
            [4290, 1139],
            [4228, 1166],
            [4174, 1192],
            [4691, 1228],
            [4477, 1335],
            [4361, 1317],
            [4352, 1335],
            [4326, 1281],
            [4628, 1077],
            [2643, 329],
            [2536, 240],
            [4397, 827],
            [4263, 810],
            [3631, 2857],
            [3471, 2919],
            [3667, 2795],
            [3525, 2741],
            [3436, 2777],
            [3329, 2750],
            [2741, 445],
        ]

        self.adj_list = self.load_adj_list()

    """Caution: Avoid executing the update function during active requests as it may cause significant delays (~20s).
    If any modifications need to be made to the adj_list, it is essential to ensure that the
    adj_list is updated accordingly,
    including the distances between nodes.
    """

    # noqa: C901
    def update(self):
        for x in self.adj_list:
            if type(x) != str:
                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = m.sqrt(
                            abs(
                                0.001
                                * (
                                    (self.coordinates[x][0] - self.coordinates[y][0])
                                    ** 2
                                    + (self.coordinates[x][1] - self.coordinates[y][1])
                                    ** 2
                                )
                            )
                        )
                    else:
                        try:
                            x_cor = Location.objects.filter(name=y)[0].pixel_x
                            y_cor = Location.objects.filter(name=y)[0].pixel_y
                            if x_cor is None or y_cor is None:
                                x_cor = 0
                                y_cor = 0
                        except IndexError:
                            x_cor = 0
                            y_cor = 0

                        self.adj_list[x][y] = m.sqrt(
                            abs(
                                0.001
                                * (
                                    (self.coordinates[x][0] - x_cor) ** 2
                                    + (self.coordinates[x][1] - y_cor) ** 2
                                )
                            )
                        )

            else:
                try:
                    loc = Location.objects.filter(name=x)[0]
                    x_cor = loc.pixel_x
                    y_cor = loc.pixel_y
                    if x_cor is None or y_cor is None:
                        x_cor = 0
                        y_cor = 0

                except IndexError:
                    x_cor = 0
                    y_cor = 0

                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = m.sqrt(
                            abs(
                                0.001
                                * (
                                    (x_cor - (self.coordinates[y][0])) ** 2
                                    + (y_cor - (self.coordinates[y][1])) ** 2
                                )
                            )
                        )
                    else:
                        try:
                            x_pix = Location.objects.filter(name=y)[0].pixel_x
                            y_pix = Location.objects.filter(name=y)[0].pixel_y

                        except IndexError:
                            x_pix = 0
                            y_pix = 0
                        if x_pix is None or y_pix is None:
                            x_pix = 0
                            y_pix = 0

                        self.adj_list[x][y] = m.sqrt(
                            abs(0.001 * ((x_cor - x_pix) ** 2 + (y_cor - y_pix) ** 2))
                        )
            # Need to run this once to update the database with given new or updated node points.
            i = 0
            loc_list = []
            for p in self.coordinates:
                loc, c = Location.objects.get_or_create(
                    pixel_x=p[0], pixel_y=p[1], name="Node" + str(i)
                )
                loc_list.append(loc)
                i += 1

            adj_list_path = f"{os.getcwd()}/locations/management/commands/adj_list.py"

            with open(adj_list_path, "w") as f:
                f.write(str(self.adj_list))

    """
    Updates the 'connected_locs' field of Location objects with conected locations
    """

    def update_locations_with_connected_loc(self):
        # Need to run this to ensure the location objects contain the adjacent locations that they are connected to.
        all_locations = Location.objects.all()
        for location in all_locations:
            try:
                adj_locs_dict = self.adj_list[location.name]
                connected_location_str = ""
                for i in adj_locs_dict:
                    if isinstance(i, int):
                        connected_location_str += f"Node{i},"
                    else:
                        connected_location_str += f"{i},"
                connected_location_str.replace(connected_location_str[-1], "", 1)
                location.connected_locs = connected_location_str
                location.save()
            except KeyError:
                pass

    """Gets the nearest Node near a location on the map."""

    def load_adj_list(self):
        adj_list_path = f"{os.getcwd()}/locations/management/commands/adj_list.py"
        adj_list = {}

        with open(adj_list_path, "r") as f:
            adj_list = dict(eval(f.read()))

        return adj_list

    import sys

    def get_nearest(self, loc):
        if "Node" in loc:
            k = int(loc.replace("Node", ""))
            return k

        min_dist = sys.maxsize
        nearest_loc = None

        try:
            sets = self.adj_list[loc]
            for i in sets:
                if isinstance(i, int):
                    if sets[i] <= min_dist:
                        min_dist = sets[i]
                        nearest_loc = i
        except KeyError:
            print(f"This Location: {loc} does not exist in adj_list")

        return nearest_loc

    """Returns the adj_list which contains only the node points containing the endpoint and the start point"""

    def graph(self, end, start):
        new_adjoint_list = {}
        for i in self.adj_list:
            if isinstance(i, int) or i == start or i == end:
                new_adjoint_list[i] = {}
                for j in self.adj_list[i]:
                    if isinstance(j, int) or j == start or j == end:
                        new_adjoint_list[i][j] = self.adj_list[i][j]

        return new_adjoint_list

    @staticmethod
    def location_location_distance(location1, location2):
        loc1 = Location.objects.filter(name=location1)[0]
        loc2 = Location.objects.filter(name=location2)[0]

        x_loc1 = loc1.pixel_x
        y_loc1 = loc1.pixel_y
        x_loc2 = loc2.pixel_x
        y_loc2 = loc2.pixel_y

        lld = abs(0.001 * ((x_loc1 - x_loc2) ** 2 + (y_loc1 - y_loc2) ** 2))
        return lld


def dijkstra(graph, start, goal):
    shortest_dist = {}
    track_pred = {}
    unseenNodes = graph
    inf = sys.maxsize
    track_path = []
    for node in unseenNodes:
        shortest_dist[node] = inf
    shortest_dist[start] = 0
    while unseenNodes:
        min_distNode = None
        for node in unseenNodes:
            if min_distNode is None:
                min_distNode = node
            elif shortest_dist[node] < shortest_dist[min_distNode]:
                min_distNode = node
        path_options = graph[min_distNode].items()
        for child_node, weight in path_options:
            if weight + shortest_dist[min_distNode] < shortest_dist[child_node]:
                shortest_dist[child_node] = weight + shortest_dist[min_distNode]
                track_pred[child_node] = min_distNode
        unseenNodes.pop(min_distNode)
    currentNode = goal
    while currentNode != start:
        try:
            track_path.insert(0, currentNode)
            currentNode = track_pred[currentNode]
        except KeyError:
            print(f"Path is not reachable start : {start}, end: {goal}")

            return None
    track_path.insert(0, start)
    if shortest_dist[goal] != inf:
        print(str(shortest_dist[goal]))
        print(str(track_path))

        return track_path

    # for i in range(0, len(coordinates)):
    #     loc1 = loc_list[i]
    #     print(adj_list[i])
    #     for loc2_ind in adj_list[i]:
    #         loc2 = loc_list[loc2_ind]
    #         dist = adj_list[i][loc2_ind]
    #         lld = LocationLocationDistance.objects.filter(location1__id=loc1.id, location2__id=loc2.id).first()
    #         if not lld:
    #             LocationLocationDistance.objects.create(
    #                 location1=loc1, location2=loc2, distance=dist)
    #         else:
    #             lld.distance = dist
    #             lld.save()


class Command(BaseCommand):
    help = "Updates the external blog database"

    def handle(self, *args, **options):
        """Run the chore."""

        handle_entry(settings.EXTERNAL_BLOG_URL)
        self.stdout.write(
            self.style.SUCCESS("External Blog Chore completed successfully")
        )


""" This command gets the nearest points for some x,y coordinates. Although a simliar function is defined in views.py"""


def fn_nearest_points(request):
    xcor = request.data2["xcor"]
    ycor = request.data2["ycor"]

    locations = {}
    if xcor is not None and ycor is not None:
        try:
            xcor = int(xcor)
            ycor = int(ycor)
        except TypeError:
            data = {"detail": "Invalid Coordinates "}
            return data
        if "only_nodes" in request.data2:
            filtered_locations = Location.objects.filter(
                Q(name__contains="Node"),
                pixel_x__range=[xcor - 1200, xcor + 1200],
                pixel_y__range=[ycor - 1200, ycor + 1200],
            )
            # filtered_locations = location.filter
            # (pixel_x__range=[xcor - 400, xcor +   # 400], pixel_y__range=[ycor - 400, ycor # + 400])
        else:
            location = Location
            filtered_locations = location.objects.filter(
                pixel_x__range=[xcor - 400, xcor + 400],
                pixel_y__range=[ycor - 400, ycor + 400],
            )
        if len(filtered_locations) >= 2:
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist = sys.maxsize
            npi = 0
            snpi = 1
            for a in range(0, len(filtered_locations) - 1):
                i = filtered_locations[a]
                distance = 0.001 * ((i.pixel_x - xcor) ^ 2 + (i.pixel_y - ycor) ^ 2)
                if distance <= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi = a
                    nearest_point_dist = distance
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a

        elif len(filtered_locations) < 2:
            filtered_locations = Location.objects.filter(
                pixel_x__range=[xcor - 1200, xcor + 1200],
                pixel_y__range=[ycor - 1200, ycor + 1200],
            )
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist = sys.maxsize
            npi = 0
            snpi = 1
            for a in range(0, len(filtered_locations) - 1):
                i = filtered_locations[a]
                distance = 0.001 * ((i.pixel_x - xcor) ^ 2 + (i.pixel_y - ycor) ^ 2)
                if distance <= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi = a
                    nearest_point_dist = distance
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a
        if len(filtered_locations) >= 2:
            locations[0] = LocationSerializerMin(filtered_locations[npi]).data
            locations[1] = LocationSerializerMin(filtered_locations[snpi]).data

            return locations
        else:
            return {"detail": "No Locations"}
