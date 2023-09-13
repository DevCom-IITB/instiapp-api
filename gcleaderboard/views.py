from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from .models import GC, GC_Hostel_Points, Hostel

from rest_framework.response import Response
from .serializers import (
    GCSerializer,
    Hostel_PointsSerializer,
    Hostel_Serializer,
)


class InstiViewSet(viewsets.ModelViewSet):
    queryset = GC.objects
    serializer_class = GCSerializer
    """ GET 1> List Of Types Of GCs """

    def Types_Of_GCs(self, request):
        data = {1: "Tech", 2: "Sports", 3: "Cult"}
        return Response(data)

    """ 2> GET  List Of GCs of A Type """

    def X_GC(
        self,
        request,
        Type,
    ):
        gcs = GC.objects.filter(type=Type)
        serializer = GCSerializer(gcs, many=True)
        return Response(serializer.data)

    """ 3> GET List Of Hostel Sorted w.r.t points for LeaderBoard of That GC """

    def Sub_GC_LB(self, request, gcuuid):
        gc = GC_Hostel_Points.objects.filter(gc__id=gcuuid).order_by("-points")
        serializer = Hostel_PointsSerializer(gc, many=True)
        return Response(serializer.data)

    """ GET 4> Leaderboard for list of hostels for types of GC """

    def Type_GC_LB(self, request, Type):
        data = {}
        all_rows = Hostel.objects.all()
        for row in all_rows:
            # Access fields of the row
            curr_hostel_name = row.short_name

            Total_Points_Curr_Hostel = GC_Hostel_Points.objects.filter(
                hostel__short_name=curr_hostel_name, gc__type=Type
            ).aggregate(Total_Points=Coalesce(Sum("points"), Value(0)))["Total_Points"]

            data.update({curr_hostel_name: Total_Points_Curr_Hostel})

        sorted_dict = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        print(sorted_dict)
        return Response(sorted_dict)

    """GET  5 List of Hostels for overall Leaderboard """

    def GC_LB(self, request):
        data = {}
        all_rows = Hostel.objects.all()
        for row in all_rows:
            curr_hostel_name = row.short_name

            Total_Points_Curr_Hostel = GC_Hostel_Points.objects.filter(
                hostel__short_name=curr_hostel_name
            ).aggregate(Total_Points=Coalesce(Sum("points"), Value(0)))["Total_Points"]

            data.update({curr_hostel_name: Total_Points_Curr_Hostel})

        sorted_dict = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

        print(sorted_dict)
        return Response(sorted_dict)


class PostViewSet(viewsets.ModelViewSet):
    queryset = GC.objects.all()  
    serializer_class = GCSerializer

    """ POST 6> Add GC  """
    def add_GC(self, request):
        serializer = GCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class UpdateViewSet(viewsets.ModelViewSet):
    queryset = GC_Hostel_Points.objects.all()  
    serializer_class = Hostel_Serializer

    """ PUT 7> Modify Hostel Points for a GC  """

    def update_Points(self, request, pk):
        hostel = GC_Hostel_Points.objects.get(id=pk)
        change_point = int(request.data["points"])
        hostel.points += change_point
        hostel.save()
        return Response({"message": "Points updated"})
