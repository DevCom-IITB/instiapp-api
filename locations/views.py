"""Views for locations app."""
import sys
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from roles.helpers import insti_permission_required
from roles.helpers import login_required_ajax
from roles.helpers import user_has_insti_privilege
from roles.helpers import user_has_privilege
from roles.helpers import forbidden_no_privileges
from django.db.models import Q
from django.http import HttpRequest
from locations.serializers import LocationSerializer
from locations.models import Location
from locations.management.commands.mapnav import (
    handle_entry,
    dijkstra,
)


class LocationViewSet(viewsets.ModelViewSet):
    """Location"""

    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @staticmethod
    def list(request):
        """List reusable locations."""
        queryset = Location.objects.filter(reusable=True)

        # Check if we don't want residences
        exclude = request.GET.get("exclude_group")
        if exclude is not None:
            queryset = queryset.exclude(group_id=int(exclude))

        return Response(LocationSerializer(queryset, many=True).data)

    @insti_permission_required("Location")
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
        if user_has_insti_privilege(request.user.profile, "Location"):
            return super().update(request, pk)

        # Disallow modifying reusable locations or marking reusable
        location = Location.objects.get(id=pk)
        if "reusable" in request.data:
            if (request.data["reusable"] != location.reusable) or location.reusable:
                return forbidden_no_privileges()

        # Check if user has update privileges for each associated event
        for event in location.events.all():
            can_update = any(
                [
                    user_has_privilege(request.user.profile, str(b.id), "UpdE")
                    for b in event.bodies.all()
                ]
            )
            if not can_update:
                return forbidden_no_privileges()

        return super().update(request, pk)

    @insti_permission_required("Location")
    def destroy(self, request, pk):
        """Delete a Location.
        Needs 'Location' institute permission."""

        return super().destroy(request, pk)


"""
This endpoint gives the shortest path between two points on the map in a sequence of locations.
"""


@api_view(("POST",))
def get_shortest_path(request):
    try:
        start = request.data["origin"]
        formatted_origin = True
    except KeyError:
        start_x = (request.data["start"])["x_coordinate"]
        start_y = (request.data)["start"]["y_coordinate"]
        formatted_origin = False

        data2 = {"xcor": str(start_x), "ycor": str(start_y)}
        request2 = HttpRequest()
        request2.data2 = data2
        # start = fn_nearest_points(request2)[0]["name"]
    end = request.data["destination"]
    dest = end
    object = handle_entry()
    # object.update()
    strt = start
    graph = object.graph(end, start)
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
        loc_path = []

        if path is not None:
            if formatted_origin:
                loc_path.append(
                    [
                        LocationSerializer(Location.objects.get(name=strt)).data[
                            "pixel_x"
                        ],
                        LocationSerializer(Location.objects.get(name=strt)).data[
                            "pixel_y"
                        ],
                    ]
                )

            for a in range(len(path)):
                i = path[a]
                if type(i) == str:
                    loc_i = Location.objects.get(name=i)
                else:
                    name = "Node" + str(i)
                    loc_i = Location.objects.get(name=name)
                loc_path.append(
                    [
                        LocationSerializer(loc_i).data["pixel_x"],
                        LocationSerializer(loc_i).data["pixel_y"],
                    ]
                )
            loc_path.append(
                [
                    LocationSerializer(Location.objects.get(name=dest)).data["pixel_x"],
                    LocationSerializer(Location.objects.get(name=dest)).data["pixel_y"],
                ]
            )

            return Response(loc_path)
        return Response(data={"detail": "No path found"})
    return Response()


"""
Finding the nearest two points for a given set of coordinates.
"""


@api_view(("POST",))
def nearest_points(request):
    xcor = request.data["xcor"]
    ycor = request.data["ycor"]

    locations = {}
    if xcor is not None and ycor is not None:
        try:
            xcor = int(xcor)
            ycor = int(ycor)
        except TypeError:
            data = {"detail": "Invalid Coordinates "}
            return Response(data=data)
        if "only_nodes" in request.data:
            filtered_locations = Location.objects.filter(
                Q(name__contains="Node"),
                pixel_x__range=[xcor - 1200, xcor + 1200],
                pixel_y__range=[ycor - 1200, ycor + 1200],
            )
            # filtered_locations = location.filter(
            # pixel_x__range=[xcor - 400, xcor + 400], pixel_y__range=[ycor - 400, ycor + 400])
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
            locations[0] = LocationSerializer(filtered_locations[npi]).data
            locations[1] = LocationSerializer(filtered_locations[snpi]).data

            return Response(data=locations)
        else:
            return Response(data={"detail": "No Locations"})


"""
"Testing errors in the adjacency list:
These are the errors that may occur when running the Dijkstra code. It provides common error outputs."
"""


@api_view(["GET"])
def checkerrors(request):
    adj_list = handle_entry().load_adj_list()  # change this list accordingly
    # adj_list ={}
    items = {}
    items["Failed : Location Does Not Exist"] = []
    items["Failed : MultipleObjectsReturned"] = []

    items["Passed : Coordinates null"] = []
    items["Passed : Coordinates are null"] = []

    for x in adj_list:
        if isinstance(x, str):
            try:
                a = Location.objects.get(name=x)
                if a.pixel_x is None or a.pixel_y is None:
                    ser = LocationSerializer(a)
                    items["Passed : Coordinates null"].append(x)
            except Location.DoesNotExist:
                items["Failed : Location Does Not Exist"].append(x)
            except Location.MultipleObjectsReturned:
                items["Failed : MultipleObjectsReturned"].append(x)

        for y in adj_list[x]:
            if isinstance(y, str):
                try:
                    a = Location.objects.get(name=y)
                    if a.pixel_x is None or a.pixel_y is None:
                        ser = LocationSerializer(a)
                        items["Passed : Coordinates are null"] = ser.data
                except Location.DoesNotExist:
                    items["Failed : Location Does Not Exist"].append(y)
                except Location.MultipleObjectsReturned:
                    items["Failed : MultipleObjectsReturned"].append(y)
    return Response(data=items)


# test
@api_view(["GET", "POST"])
def allnodes(request):
    all_nodes = []
    for a in range(0, 246):
        node = "Node" + str(a)
        all_nodes.append(
            [
                LocationSerializer(Location.objects.get(name=node)).data["pixel_x"],
                LocationSerializer(Location.objects.get(name=node)).data["pixel_y"],
            ]
        )

    return Response(data=all_nodes)
