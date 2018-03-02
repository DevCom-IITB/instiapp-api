from django.shortcuts import render
from rest_framework import viewsets
from bodies.serializers import BodySerializer
from bodies.models import Body, BodyChildRelation

class BodyViewSet(viewsets.ModelViewSet):
    ' API endpoint that allows bodies to be viewed or edited '
    queryset = Body.objects.all()
    serializer_class = BodySerializer

    def get_serializer_context(self):
        return {'request': self.request}
