"""Views for locations app."""
from rest_framework import viewsets
from rest_framework.response import Response
from locations.serializers import LocationSerializer
from locations.models import Location
from roles.helpers import insti_permission_required
from roles.helpers import login_required_ajax
from roles.helpers import user_has_insti_privilege
from roles.helpers import user_has_privilege
from roles.helpers import forbidden_no_privileges
import sys
from rest_framework.decorators import api_view
from locations.management.commands.krishna import handle_entry, dijkstra

class LocationViewSet(viewsets.ModelViewSet):
    """Location"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @staticmethod
    def list(request):
        """List reusable locations."""
        queryset = Location.objects.filter(reusable=True)

        # Check if we don't want residences
        exclude = request.GET.get('exclude_group')
        if exclude is not None:
            queryset = queryset.exclude(group_id=int(exclude))

        return Response(LocationSerializer(queryset, many=True).data)

    @insti_permission_required('Location')
    def create(self, request):
        """Create a Location.
        Needs 'Location' institute permission."""

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update Location.
        This requires the user to have the 'Location' institute permission
        or BodyRole for the event using the location if the it is not reusable."""

        # Allow insti privelege to do anything
        if user_has_insti_privilege(request.user.profile, 'Location'):
            return super().update(request, pk)

        # Disallow modifying reusable locations or marking reusable
        location = Location.objects.get(id=pk)
        if 'reusable' in request.data:
            if (request.data['reusable'] != location.reusable) or location.reusable:
                return forbidden_no_privileges()

        # Check if user has update privileges for each associated event
        for event in location.events.all():
            can_update = any([user_has_privilege(
                request.user.profile, str(b.id), 'UpdE') for b in event.bodies.all()])
            if not can_update:
                return forbidden_no_privileges()

        return super().update(request, pk)

    @insti_permission_required('Location')
    def destroy(self, request, pk):
        """Delete a Location.
        Needs 'Location' institute permission."""

        return super().destroy(request, pk)


''' 
This endpoint gives the shortest path between two points on the map in a sequence of locations.
'''

<<<<<<< HEAD
@api_view(('POST',))
def get_shortest_path(request):
    try:
        start = request.data['origin']
    except IndexError:
        start_x = request.data["start"]["x_coordinate"]
        start_y = request.data["start"]["y_coordinate"]
        data = {"xcor": start_x,
                "ycor":start_y}
        start = nearest_points(data)[0]["name"]
        
            
        
    end = request.data['destination']
=======
@api_view(('GET',))
def get_shortest_path(request):
    start = request.GET.get('origin')
    end = request.GET.get('destination')
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
    graph = handle_entry() # This is to update the adj_list along with the distances. And update the database
    if start is not None and end is not None:
        try:
            start = int(start)
        except ValueError:
            pass
        try:
            end = int(end)
        except ValueError:
            pass
        try:
            path = dijkstra(graph, start, end)
        except KeyError:
            return Response(data=[])
<<<<<<< HEAD
        loc_path = []
=======
        loc_path = {}
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
        
        if path is not None:
            for a in range(len(path)):
                i = path[a]
                if type(i) == str:
                    loc_i = Location.objects.get(name=i)
                else:
                    name = "Node"+str(i)
                    loc_i = Location.objects.get(name = name)
<<<<<<< HEAD
                loc_path.append([LocationSerializer(loc_i).data["pixel_x"],
                                LocationSerializer(loc_i).data["pixel_y"]
                                             ])
            return Response(loc_path)

=======
                loc_path[a] = LocationSerializer(loc_i).data
        
        return Response(loc_path)
            
 
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
    return Response()

'''
Finding the nearest two points for a given set of coordinates. 
'''
<<<<<<< HEAD
@api_view(("POST",))
def nearest_points(request):
    xcor = request.data["xcor"]
    ycor = request.data["ycor"]
=======
@api_view(("GET",))
def nearest_points(request):
    xcor = request.GET.get("xcor")
    ycor = request.GET.get("ycor")
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3

    locations ={}
    if xcor is not None and ycor is not None:
        try:
            xcor = int(xcor)
            ycor = int(ycor)
        except TypeError:
            data= {"detail" :"Invalid Coordinates "}
            return Response(data=data)

<<<<<<< HEAD
        filtered_locations = Location.objects.filter(pixel_x__range =[xcor-400, xcor+400],pixel_y__range=[ycor-400, ycor+400] )
=======
        filtered_locations = Location.objects.filter(pixel_x__range =[xcor-100, xcor+100],pixel_y__range=[ycor-100, ycor+100] )
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
        if len(filtered_locations)>=2:
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist =sys.maxsize
            npi =0
            snpi =1
            for a in range(0,len(filtered_locations)-1):
                i = filtered_locations[a]
                distance = 0.001*((i.pixel_x-xcor)^2+(i.pixel_y-ycor)^2)
                if distance<= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi =a
                    nearest_point_dist = distance
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a

        elif len(filtered_locations)<2:
<<<<<<< HEAD
            filtered_locations = Location.objects.filter(pixel_x__range =[xcor-1200, xcor+1200],pixel_y__range=[ycor-1200, ycor+1200] )
=======
            filtered_locations = Location.objects.filter(pixel_x__range =[xcor-400, xcor+400],pixel_y__range=[ycor-400, ycor+400] )
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist =sys.maxsize
            npi =0
            snpi =1
            for a in range(0,len(filtered_locations)-1):
                i = filtered_locations[a]
                distance = 0.001*((i.pixel_x-xcor)^2+(i.pixel_y-ycor)^2)
                if distance<= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi =a
                    nearest_point_dist = distance    
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a        
        if len(filtered_locations)>=2:
            locations[0] = LocationSerializer(filtered_locations[npi]).data
            locations[1] = LocationSerializer(filtered_locations[snpi]).data

            return Response(data=locations)
        else:
                return Response(data={"detail":"No Locations"})
        




'''
Testing errors in adj_list:
This gives errors that we might get once djisktra code is run. It outputs some common errors.


'''
@api_view(["GET"])
def checkerrors(request):

    adj_list = {
        0: {
            2: -1,
            "Main Gate no. 2": -1,
            "State Bank of India, IIT Powai branch": -1,
            "Bungalow A8 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A6 ": -1,
        },
        "Main Gate no. 2": {0: -1},
        "State Bank of India, IIT Powai branch": {0: -1},
        "Bungalow A8 ": {0: -1, 1: -1, 49: -1},
        "Bungalow A7 ": {0: -1, 1: -1, 49: -1},
        "Bungalow A6 ": {0: -1, 1: -1, 49: -1},
        1: {
            2: -1,
            3: -1,
            22: -1,
            "Shishu Vihar": -1,
            "Bungalow A8 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A6 ": -1,
            "Bungalow A4 ": -1,
            "Bungalow A3 ": -1,
            "Bungalow A2 ": -1,
            "A1 Director Bungalow": -1,
            49: -1,
        },
        "Shishu Vihar": {1: -1, 49: -1},
        "Bungalow A4 ": {1: -1, 4: -1, 50: -1},
        "Bungalow A3 ": {1: -1, 4: -1, 50: -1},
        "Bungalow A2 ": {1: -1, 4: -1, 50: -1},
        "A1 Director Bungalow": {1: -1, 4: -1, 51: -1},
        2: {
            0: -1,
            22: -1,
            21: -1,
            1: -1,
            "Type B-8": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
        },
        "Type B-8": {2: -1, 3: -1, 22: -1},
        "Type B-7": {2: -1, 3: -1, 21: -1, 22: -1},
        "Type B-9": {2: -1, 3: -1, 22: -1, 23: -1},
        "Type B-10": {2: -1, 3: -1, 22: -1, 23: -1},
        3: {
            1: -1,
            4: -1,
            5: -1,
            23: -1,
            "Hostel 10 Annexe (Girls Hostel)": -1,
            "Hostel 10 Phoenix (Girls Hostel)": -1,
            "Type B-8": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
        },
        "Hostel 10 Annexe (Girls Hostel)": {3: -1, 5: -1},
        "Hostel 10 Phoenix (Girls Hostel)": {3: -1, 5: -1},
        4: {
            3: -1,
            5: -1,
            "Bungalow A4 ": -1,
            "Bungalow A3 ": -1,
            "Bungalow A2 ": -1,
            "A1 Director Bungalow": -1,
            "Type B-1": -1,
            51: -1,
        },
        "Type B-1": {4: -1, 51: -1},
        5: {4: -1, 6: -1, "Gulmohar Restaurant": -1, "Hostel 10 Annexe (Girls Hostel)": -1, "Hostel 10 Phoenix (Girls Hostel)": -1, 54: -1, 55: -1},
        "Gulmohar Restaurant": {5: -1, 54: -1},
        6: {
            5: -1,
            7: -1,
            20: -1,
            "B 24 Nilgiri": -1,
            "Type B-18": -1,
            "Type B-17": -1,
            "Type C-2": -1,
        },
        "B 24 Nilgiri": {6: -1},
        "Type B-18": {6: -1, 20: -1},
        "Type B-17": {6: -1, 20: -1},
        "Type C-2": {6: -1, 20: -1},
        7: {6: -1, 8: -1, 14: -1, "Type C-5": -1, "B 21 Satpura": -1, 95: -1, 96: -1},
        "Type C-5": {7: -1, 14: -1},
        "B 21 Satpura": {7: -1, 14: -1},
        8: {7: -1, 9: -1, 96: -1},
        9: {
            8: -1,
            10: -1,
            83: -1,
            "Kendriya Vidyalaya ": -1,
            "DESE & CESE New Building": -1,
            "Type1 - 1": -1,
            "Type1 - 2": -1,
            "Type1 - 3": -1,
            "Type1 - 4": -1,
            "Cafe Coffee Day": -1
        },
        "Kendriya Vidyalaya ": {9: -1, 10: -1},
        "DESE & CESE New Building": {9: -1},
        "Type1 - 1": {9: -1},
        "Type1 - 2": {9: -1},
        "Type1 - 3": {9: -1},
        "Type1 - 4": {9: -1},
        10: {9: -1, 11: -1, 12: -1, "Kendriya Vidyalaya ": -1, "Medical Store": -1, "Post Office": -1},
        "Medical Store": {10: -1},
        "Post Office": {10: -1, 12: -1},
        11: {10: -1, "Uphar": -1},
        "Uphar": {11: -1},
        12: {10: -1, 13: -1, "Market Gate, Y point Gate no. 3": -1, "Post Office": -1},
        "Market Gate, Y point Gate no. 3": {12: -1},
        13: {
            12: -1,
            14: -1,
            15: -1,
            "Kendriya Vidyalay Quarters 1": -1,
            "Kendriya Vidyalay Quarters 2": -1,
            "Type C-6": -1,
        },
        "Kendriya Vidyalay Quarters 1": {13: -1},
        "Kendriya Vidyalay Quarters 2": {13: -1},
        "Type C-6": {13: -1, 14: -1},
        14: {
            7: -1,
            13: -1,
            "Type C-5": -1,
            "B 21 Satpura": -1,
            "Type C-7": -1,
            "Type C-6": -1,
            "Shivalik C 23 (187-240)": -1,
        },
        "Type C-7": {14: -1},
        "Shivalik C 23 (187-240)": {14: -1},
        15: {
            13: -1,
            16: -1,
            "Type C-18": -1,
            "Campus School": -1,
            "Type C-17": -1,
            "Type C-15": -1,
        },
        "Type C-18": {15: -1},
        "Campus School": {15: -1, 16: -1},
        "Type C-17": {15: -1, 16: -1},
        "Type C-15": {15: -1, 16: -1},
        16: {
            15: -1,
            17: -1,
            18: -1,
            "Campus School": -1,
            "Type C-17": -1,
            "Type C-15": -1,
            "Type C-16": -1,
            "Type C-14": -1,
            "Type C-13": -1,
        },
        "Type C-16": {16: -1},
        "Type C-14": {16: -1},
        "Type C-13": {16: -1, 17: -1},
        17: {16: -1, 19: -1, "Type C-13": -1},
        18: {16: -1, 19: -1, "Type C-8": -1},
        "Type C-8": {18: -1},
        19: {
            17: -1,
            18: -1,
            20: -1,
            21: -1,
            22: -1,
            "Type C-9": -1,
            "Type C-12": -1,
            "Type C-11": -1,
            "Type C-10": -1,
        },
        "Type C-9": {19: -1},
        "Type C-12": {19: -1, 21: -1},
        "Type C-11": {19: -1, 21: -1},
        "Type C-10": {19: -1, 20: -1, 22: -1},
        20: {
            23: -1,
            6: -1,
            22: -1,
            19: -1,
            18: -1,
            "Type C-10": -1,
            "Type C-2": -1,
            "Type B-17": -1,
            "Type B-18": -1,
        },
        21: {
            2: -1,
            22: -1,
            19: -1,
            17: -1,
            "Type B-5": -1,
            "Type B-6": -1,
            "Type C-11": -1,
            "Type B-7": -1,
            "Type B-4": -1,
            "Type C-12": -1,
        },
        "Type B-5": {21: -1, 22: -1},
        "Type B-6": {21: -1},
        "Type B-4": {21: -1, 22: -1},
        22: {
            1: -1,
            2: -1,
            19: -1,
            21: -1,
            23: -1,
            20: -1,
            18: -1,
            "Type B-8": -1,
            "Type B-2": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
            "Type B-3": -1,
            "Type B-4": -1,
            "Type B-5": -1,
            "Type C-10": -1,
        },
        "Type B-2": {22: -1, 23: -1},
        "Type B-3": {22: -1, 23: -1},
        23: {
            3: -1,
            20: -1,
            22: -1,
            "Type B-9": -1,
            "Type B-2": -1,
            "Type B-10": -1,
            "Type B-3": -1,
        },
        24: {
            "Mess for hostels 12 | 13 | 14": -1,
            "Hostel 12 Crown of the Campus": -1,
            "Hostel 13 House of Titans": -1,
            "Hostel 14 Silicon Ship": -1,
            25: -1,
            "Security Check Point": -1,
        },
        "Mess for hostels 12 | 13 | 14": {24: -1},
        "Hostel 12 Crown of the Campus": {24: -1},
        "Hostel 13 House of Titans": {24: -1},
        "Hostel 14 Silicon Ship": {24: -1},
        "Security Check Point": {24: -1},
        25: {
            "Hostel 06 Vikings": -1,
            "Hostel 07 Lady of the Lake": -1,
            "Hostel 09 Nawaabon Ki Basti": -1,
            "ATM - Canara Bank near H6": -1,
            24: -1,
            26: -1,
            "Type1 - 22": -1,
            "Hostel 18": -1,
            "Hostel 17": -1
        },
        "Hostel 06 Vikings": {25: -1},
        "Hostel 07 Lady of the Lake": {25: -1},
        "Hostel 09 Nawaabon Ki Basti": {25: -1},
        "ATM - Canara Bank near H6": {25: -1},
        "Type1 - 22": {25: -1},
        "Hostel 18": {25: -1, 26: -1},
        26: {"Hostel 05 Penthouse": -1, 27: -1, 34: -1, "Hostel 18": -1, "Chaayos Cafe": -1, "Hostel 17": -1},
        "Hostel 05 Penthouse": {26: -1},
        27: {
            26: -1,
            28: -1,
            35: -1,

            "Gymkhana Grounds": -1,
            "Gymkhana Building": -1,
            "Basketball Court": -1,
            "Hostel 11 Athena (Girls Hostel)": -1,
            "Brewberrys Cafe": -1,
        },
        "Gymkhana Grounds": {27: -1, 28: -1},
        "Gymkhana Building": {27: -1, 28: -1},
        "Basketball Court": {27: -1, 28: -1},
        "Hostel 11 Athena (Girls Hostel)": {27: -1, 28: -1},
        "Brewberrys Cafe": {27: -1, 28: -1},
        28: {
            27: -1,
            70: -1,
            "Gymkhana Grounds": -1,
            "Gymkhana Building": -1,
            "Basketball Court": -1,
            "Hostel 11 Athena (Girls Hostel)": -1,
            "Brewberrys Cafe": -1,
            "Staff Hostel": -1,
            "Tennis Court (new)": -1,
            "Squash Court": -1,
            "Tennis Court (old)": -1,
            "Hockey Ground": -1,
        },
        "Staff Hostel": {28: -1},
        "Tennis Court (new)": {28: -1},
        "Squash Court": {28: -1},
        "Tennis Court (old)": {28: -1},
        "Hockey Ground": {28: -1},
        29: {30: -1, "State Bank of India Branch": -1, "Bungalow A14 ": -1, "Bungalow A15 ": -1, 69: -1, "Dominoes outlet": -1},
        "State Bank of India Branch": {29: -1},
        "Bungalow A14 ": {29: -1},
        "Bungalow A15 ": {29: -1},
        30: {
            29: -1,
            31: -1,
            32: -1,
            "Bungalow A16 ": -1,
            "Bungalow A17 ": -1,
            "Bungalow A18 ": -1,
            "Bungalow A19 ": -1,
            "Defence Research & Development Organization": -1,
        },
        "Bungalow A16 ": {30: -1},
        "Bungalow A17 ": {30: -1},
        "Bungalow A18 ": {30: -1},
        "Bungalow A19 ": {30: -1},
        "Defence Research & Development Organization": {30: -1},
        31: {30: -1, "Hostel 15 Trident": -1, "Hostel 16 Olympus": -1, "B 23 Aravali": -1, "Society for Applied Microwave Electronics Engineering & Research": -1},
        "Hostel 15 Trident": {31: -1},
        "Hostel 16 Olympus": {31: -1},
        "B 23 Aravali": {31: -1},
        "Society for Applied Microwave Electronics Engineering & Research": {31: -1},
        32: {30: -1, 33: -1, "Hostel 01 Queen of the campus": -1},
        "Hostel 01 Queen of the campus": {32: -1},
        33: {32: -1, 34: -1, "Indoor Stadium": -1, "Students Activity Centre": -1, "Hostel 02 The Wild Ones": -1, "Swimming Pool (new)": -1},
        "Indoor Stadium": {33: -1},
        "Students Activity Centre": {33: -1},
        "Hostel 02 The Wild Ones": {33: -1},
        "Swimming Pool (new)": {33: -1},
        34: {
            33: -1,
            "Outdoor Sports Facility": -1,
            "Hostel 04 MadHouse": -1,
            "Tansa House King of campus (Proj. Staff Boys)": -1,
            26: -1,
            "Hostel 03 Vitruvians": -1,
            "Type1 - 11": -1,
        },
        "Outdoor Sports Facility": {34: -1},
        "Hostel 04 MadHouse": {34: -1},
        "Tansa House King of campus (Proj. Staff Boys)": {34: -1},
        "Hostel 03 Vitruvians": {34: -1},
        "Type1 - 11": {34: -1},
        35: {36: -1, 27: -1},
        36: {35: -1, 37: -1},
        37: {36: -1, 38: -1},
        38: {"Boat House": -1, 37: -1, 39: -1},
        "Boat House": {38: -1},
        39: {38: -1, 40: -1},
        40: {39: -1, 41: -1},
        41: {
            40: -1,
            42: -1,
            "National Centre for Mathematics": -1,
            "Kshitij Udyan": -1,
            "Guest House / Padmavihar": -1,
            "Guest House / Jalvihar": -1,
        },
        "National Centre for Mathematics": {41: -1},
        "Kshitij Udyan": {41: -1},
        "Guest House / Padmavihar": {41: -1},
        "Guest House / Jalvihar": {41: -1, 42: -1},
        42: {41: -1, 43: -1, 52: -1, "Guest House / Jalvihar": -1, "Type B-14": -1},
        "Type B-14": {42: -1},
        43: {42: -1, 44: -1},
        44: {
            43: -1,
            45: -1,
            50: -1,
            "Type B-13": -1,
            "Type B-11": -1,
            "Type B-12": -1,
            "Type B-15": -1,
            "Type B-16": -1,
        },
        "Type B-13": {44: -1},
        "Type B-11": {44: -1},
        "Type B-12": {44: -1},
        "Type B-15": {44: -1},
        "Type B-16": {44: -1},
        45: {44: -1, 46: -1},
        46: {45: -1, 47: -1, 57: -1, "B 19 Old Multistoried Building- Residence ": -1},
        "B 19 Old Multistoried Building- Residence ": {46: -1},
        47: {46: -1, 48: -1, "White House": -1, "CTR 20": -1},
        "White House": {47: -1},
        "CTR 20": {47: -1},
        48: {
            47: -1,
            49: -1,
            "CTR 19": -1,
            "Bungalow A9 ": -1,
            "Bungalow A10 ": -1,
            "BTR Building - A & B": -1,
        },
        "CTR 19": {48: -1},
        "Bungalow A9 ": {48: -1},
        "Bungalow A10 ": {48: -1},
        "BTR Building - A & B": {48: -1},
        49: {
            48: -1,
            50: -1,
            1: -1,
            "Bungalow A11 ": -1,
            "Bungalow A12 ": -1,
            "Bungalow A6 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A8 ": -1,
            "Shishu Vihar": -1,
        },
        "Bungalow A11 ": {49: -1},
        "Bungalow A12 ": {49: -1},
        50: {49: -1, 51: -1, "Bungalow A2 ": -1, "Bungalow A3 ": -1, "Bungalow A4 ": -1},
        51: {
            50: -1,
            52: -1,
            "A1 Director Bungalow": -1,
            "Bungalow A13 ": -1,
            "Type B-1": -1,
            4: -1,
        },
        "Bungalow A13 ": {51: -1},
        52: {42: -1, 51: -1, 53: -1},
        53: {52: -1, 54: -1},
        54: {53: -1, 55: -1, "Gulmohar Restaurant": -1, "Guest House / Vanvihar": -1, 5: -1},
        "Guest House / Vanvihar": {54: -1},
        55: {54: -1, 56: -1, 74: -1, "Hospital": -1, "Staff Club": -1, 5: -1},
        "Hospital": {55: -1},
        "Staff Club": {55: -1},
        56: {55: -1, 73: -1, "Convocation Hall": -1, "Type1 - 15": -1, "Type H2 - 17": -1},
        "Convocation Hall": {56: -1, 71: -1, 72: -1},
        "Type1 - 15": {56: -1},
        "Type H2 - 17": {56: -1},
        57: {46: -1, 58: -1},
        58: {57: -1, 59: -1, "Lake Side Gate no. 1": -1},
        "Lake Side Gate no. 1": {58: -1},
        59: {58: -1, 60: -1},
        60: {59: -1, 61: -1},
        61: {60: -1, "Padmavati Devi Temple": -1},
        "Padmavati Devi Temple": {61: -1},
        62: {63: -1, "OrthoCad Lab": -1, "Power House": -1, "Hostel 10A QIP (Girls Hostel)": -1},
        "OrthoCad Lab": {62: -1, 80: -1},
        "Power House": {62: -1},
        "Hostel 10A QIP (Girls Hostel)": {62: -1},
        63: {64: -1, 62: -1, "Physics Lab (Ist Years)": -1},
        "Physics Lab (Ist Years)": {63: -1},
        64: {
            65: -1,
            63: -1,
            "SMAmL Suman Mashruwala Advanced Microengineering Lab": -1,
            "Thermal Hydraulic Test Facility": -1,
        },
        "SMAmL Suman Mashruwala Advanced Microengineering Lab": {64: -1},
        "Thermal Hydraulic Test Facility": {64: -1},
        65: {
            66: -1,
            87: -1,
            64: -1,
            "Heat Transfer and Thermodynamic Lab": -1,
            "Cummins Engine Research facility": -1,
        },
        "Heat Transfer and Thermodynamic Lab": {65: -1},
        "Cummins Engine Research facility": {65: -1},
        66: {
            67: -1,
            65: -1,
            "Heat Pump Lab": -1,
            "Geotechnical Engg. Lab": -1,
            "National Geotechnical Centrifuge Facility": -1,
        },
        "Heat Pump Lab": {66: -1},
        "Geotechnical Engg. Lab": {66: -1},
        "National Geotechnical Centrifuge Facility": {66: -1},
        67: {68: -1, 88: -1, 66: -1, "Fluid Mechanics and Fluid Power Lab": -1},
        "Fluid Mechanics and Fluid Power Lab": {67: -1, 88: -1},
        68: {
            69: -1,
            67: -1,
            "Mathematics Department": -1,
            "Central Library": -1,
            90: -1,
            "Inter-disciplinary Programme in Systems and Control Engineering": -1,
            "NanoTech. & Science Research Centre": -1,
        },
        "Mathematics Department": {68: -1},
        "Central Library": {68: -1},
        "Inter-disciplinary Programme in Systems and Control Engineering": {68: -1},
        "NanoTech. & Science Research Centre": {68: -1},
        69: {70: -1, 68: -1, 29: -1},
        70: {71: -1, 69: -1, 28: -1, "NCC Office": -1},
        "NCC Office": {70: -1},
        71: {72: -1, 70: -1, "Convocation Hall": -1},
        72: {
            73: -1,
            71: -1,
            "Convocation Hall": -1,
            "Main Building": -1,
            "Staff Canteen": -1,
        },
        "Main Building": {72: -1, 76: -1},
        "Staff Canteen": {72: -1},
        73: {74: -1, 72: -1, 56: -1},
        74: {75: -1, 73: -1, 55: -1, "School of Management": -1, "Computer Centre": -1},
        "School of Management": {74: -1},
        "Computer Centre": {74: -1, 93: -1},
        75: {92: -1, 93: -1, "Girish Gaitonde Building": -1, "Seminar Hall": -1},
        "Girish Gaitonde Building": {75: -1},
        "Seminar Hall": {75: -1},
        76: {91: -1, 90: -1, 77: -1, "Main Building": -1},
        77: {89: -1, 78: -1, 76: -1, "Electrical Engineering Annexe Building": -1},
        "Electrical Engineering Annexe Building": {77: -1},
        78: {
            79: -1,
            77: -1,
            97: -1,
            "Non- Academic Staff Association": -1,
            "Victor Menezes Convention Centre": -1,
            "Industrial Design Centre": -1,
        },
        "Non- Academic Staff Association": {78: -1},
        "Victor Menezes Convention Centre": {78: -1, 97: -1},
        "Industrial Design Centre": {78: -1, 89: -1},
        79: {80: -1, 78: -1, "Structural integrity Testing and Analysis Centre": -1},
        "Structural integrity Testing and Analysis Centre": {79: -1},
        80: {
            86: -1,
            79: -1,
            62: -1,
            "Electrical Maintenence": -1,
            "Micro Fluidics Lab": -1,
            "OrthoCad Lab": -1,
        },
        "Electrical Maintenence": {80: -1},
        "Micro Fluidics Lab": {80: -1},
        81: {
            97: -1,
            82: -1,
            "Centre of Studies in Resources Engineering": -1,
            "Energy Science and Engineering": -1,
            "Earth Science Department": -1,
            "Rock Powdering Lab": -1,
        },
        "Centre of Studies in Resources Engineering": {81: -1},
        "Energy Science and Engineering": {81: -1},
        "Earth Science Department": {81: -1},
        "Rock Powdering Lab": {81: -1},
        82: {
            83: -1,
            84: -1,
            81: -1,
            "ONGC Research Centre": -1,
            "Proposed Building for Tata Centre for Technology": -1,
            "Aerospace Engineering Department": -1,
        },
        "ONGC Research Centre": {82: -1},
        "Proposed Building for Tata Centre for Technology": {82: -1, 84: -1},
        "Aerospace Engineering Department": {82: -1, 83: -1},
        83: {
            82: -1,
            9: -1,
            "Aerospace Engineering Department": -1,
            "Chemical Engineering Department": -1,
        },
        "Chemical Engineering Department": {83: -1},
        84: {85: -1, 82: -1, "Proposed Building for Tata Centre for Technology": -1},
        85: {86: -1, 84: -1},
        86: {80: -1, 85: -1, "Electrical Maintenence": -1},
        "Electrical Maintenence": {86: -1},
        87: {65: -1, "GMFL Lab / Geophysical and multiphase Flows Lab": -1},
        "GMFL Lab / Geophysical and multiphase Flows Lab": {87: -1},
        88: {
            89: -1,
            67: -1,
            "Old Computer Science Engineering Department": -1,
            "Fluid Mechanics and Fluid Power Lab": -1,
        },
        "Old Computer Science Engineering Department": {88: -1},
        89: {88: -1, "Treelabs": -1, "Industrial Design Centre": -1},
        "Treelabs": {89: -1},
        90: {68: -1, 76: -1, "Mechanical Engineering Department": -1},
        "Mechanical Engineering Department": {90: -1},
        91: {76: -1, 92: -1, "Civil Engineering Department": -1, "LTPCSA": -1},
        "Civil Engineering Department": {91: -1},
        "LTPCSA": {91: -1},
        92: {91: -1, 75: -1, "Electrical Engineering Department": -1, "Cafe 92": -1},
        "Electrical Engineering Department": {92: -1},
        93: {
            75: -1,
            94: -1,
            "Computer Centre": -1,
            "Metallurgical Engineering and Material Science Department": -1,
        },
        "Metallurgical Engineering and Material Science Department": {93: -1},
        94: {93: -1, 95: -1, "Lecture Hall Complex - 1 & 2": -1, "Kanwal Rekhi School of Information Technology": -1},
        "Lecture Hall Complex - 1 & 2": {94: -1, 96: -1},
        "Kanwal Rekhi School of Information Technology": {94: -1},
        95: {94: -1, "Physics Department": -1, 7: -1},
        "Physics Department": {95: -1},
        96: {
            77: -1,
            7: -1,
            8: -1,
            "Lecture Hall Complex - 3": -1,
            "Lecture Hall Complex - 1 & 2": -1,
            "Humanities and Social Sciences Department": -1,
            "Biosciences and Bioengineering Department": -1,
        },
        "Lecture Hall Complex - 3": {96: -1},
        "Humanities and Social Sciences Department": {96: -1},
        "Biosciences and Bioengineering Department": {96: -1},
        97: {
            78: -1,
            81: -1,
            "Victor Menezes Convention Centre": -1,
            "Centre for Environmental Science and Engineering": -1,
        },
        "Centre for Environmental Science and Engineering": {97: -1},
        "Cafe Coffee Day": {9: -1},
        "Cafe 92": {92: -1},
        "Dominoes outlet": {29: -1},
        "Chaayos Cafe": {26: -1},
        "Hostel 17": {25: -1, 26: -1}
    }
    

    items = {}
    items["Failed : Location Does Not Exist"] =[]
    items["Failed : MultipleObjectsReturned"] =[]
    items["Passed : x"] =[]
    items["Passed : y"] =[]
    items["Passed : Coordinates null"] =[]
    items["Passed : Coordinates are null"] = []
    items["Passedlo"]=[]
    for x in adj_list:
        
        if type(x)==str:
            try:
                a = Location.objects.get(name=x)
                items["Passed : x"].append(x)
                if a.pixel_x is None or a.pixel_y is None:
                    ser = LocationSerializer(a)
                    items["Passed : Coordinates null"].append(x)
            except Location.DoesNotExist:
                items["Failed : Location Does Not Exist"].append(x)
            except Location.MultipleObjectsReturned:
                items["Failed : MultipleObjectsReturned"].append(x)
                

        for y in adj_list[x]:
            if type(y) == str:
                try:
                    a = Location.objects.get(name=y)
                    items["Passed : y"].append(y)
                    if a.pixel_x is None or a.pixel_y is None:
                        ser = LocationSerializer(a)
                        items["Passed : Coordinates are null"]=ser.data
                except Location.DoesNotExist:
                    items["Failed : Location Does Not Exist"].append(y)
                except Location.MultipleObjectsReturned:
                    items["Failed : MultipleObjectsReturned"].append(y)
<<<<<<< HEAD
    return Response(data=items)

@api_view(['GET','POST'])
def allnodes(request):
    all_nodes =[]
    for a in range(0,200):
        node = "Node"+str(a)
        all_nodes.append([LocationSerializer(Location.objects.get(name=node)).data["pixel_x"],
                        LocationSerializer(Location.objects.get(name=node)).data["pixel_y"]])
    
    return Response(data=all_nodes)

=======
    return Response(data=items)
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
