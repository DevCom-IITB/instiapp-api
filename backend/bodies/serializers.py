' Serializers for Body and BodyChildRelation '
from rest_framework import serializers
from bodies.models import Body, BodyChildRelation

class BodySerializer(serializers.HyperlinkedModelSerializer):
    'Serialize Body'
    class Meta:
        model = Body
        fields = ('id', 'name', 'description', 'image_url')
