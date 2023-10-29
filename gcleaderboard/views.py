from django.shortcuts import render
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from .models import GC, GC_Hostel_Points, Hostel
from messmenu.serializers import HostelSerializer
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax

from rest_framework.response import Response
from .serializers import (
    GCSerializer,
    Hostel_PointsSerializer,
    Hostel_Serializer,
    
)

from gcleaderboard.serializers import Participants_Serializer 


class InstiViewSet(viewsets.ModelViewSet):
    queryset = GC.objects
    serializer_class = GCSerializer
  
   

    def Type_GC(
        self,
        request,
        Type,
    ):
        """  List of GCs of a particular Type """
        gcs = GC.objects.filter(type=Type)
        serializer = GCSerializer(gcs, many=True)
        return Response(serializer.data)


    def Individual_GC_LB(self, request, gc_id):
        
        """ List Of Hostels sorted w.r.t points for leaderboard of that gc """
        gc = GC_Hostel_Points.objects.filter(gc__id=gc_id).order_by("-points")
        serializer = Hostel_PointsSerializer(gc, many=True)
        return Response(serializer.data)

    

    def Type_GC_LB(self, request, Type):
        """ Leaderboard for list of hostels for types of GC """
        data = []
        all_rows = Hostel.objects.all()
        for row in all_rows:
            # Access fields of the row
            curr_hostel_id = row.id
            curr_hostel_name = row.name

            Total_Points_Curr_Hostel = GC_Hostel_Points.objects.filter(
                hostel__id=curr_hostel_id, gc__type=Type
            ).aggregate(Total_Points=Coalesce(Sum("points"), Value(0)))["Total_Points"]

            data.append({
                "hostels": HostelSerializer(row).data,
                "points": Total_Points_Curr_Hostel
            })

        sorted_dict = sorted(data, key=lambda item: item["points"], reverse=True)
        print(sorted_dict)
        return Response(sorted_dict)


    def GC_LB(self, request):
        
        """ List of Hostels for Overall Leaderboard """
        data = []
        all_rows = Hostel.objects.all()
        for row in all_rows:
            curr_hostel_id = row.id

            Total_Points_Curr_Hostel = GC_Hostel_Points.objects.filter(
                hostel__id=curr_hostel_id
            ).aggregate(Total_Points=Coalesce(Sum("points"), Value(0)))["Total_Points"]

            data.append({
                "hostels": HostelSerializer(row).data,
                "points": Total_Points_Curr_Hostel
            })

        sorted_dict = sorted(data, key=lambda item: item["points"], reverse=True)

        print(sorted_dict)
        return Response(sorted_dict)
    
    def Participants_in_GC(self ,  request , points_id ,hostel_short_name ):
         participants = GC_Hostel_Points.objects.filter(
                hostel__short_name=hostel_short_name, id = points_id
            )
         
         serializer = Participants_Serializer(participants , many = True)
         return Response(serializer.data)
         




class PostViewSet(viewsets.ModelViewSet):
    queryset = GC.objects.all()  #
    serializer_class = GCSerializer
    
    @login_required_ajax
    def add_GC(self, request):
        """ Adding New GC """
        serializer = GCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)



class UpdateViewSet(viewsets.ModelViewSet):
    queryset = GC_Hostel_Points.objects.all()  # Replace with your queryset
    serializer_class = Hostel_Serializer

    
    @login_required_ajax
    def update_Points(self, request, pk):
        """ Mpdify Hostel Points for a GC  """
        hostel = GC_Hostel_Points.objects.get(id=pk)
        change_point = int(request.data["points"])
        hostel.points += change_point
        hostel.save()
        return Response({"message": "Points updated"})
