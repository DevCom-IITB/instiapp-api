' Serializers for Body and BodyChildRelation '
from rest_framework import serializers
from rest_framework.reverse import reverse
from bodies.models import Body, BodyChildRelation

class ParentBodyHyperlink(serializers.HyperlinkedRelatedField):
    ' Gets hyperlinks for parent bodies from BodyChildRelation'
    view_name = 'body-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {'pk': obj.parent.pk}
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

class ChildrenSerializer(serializers.ModelSerializer):
    ' Serializes children of the body from BodyChildRelation'
    def to_representation(self, value):
        return BodySerializer(value.child, context=self.context).data

class BodySerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Body'

    parents = ParentBodyHyperlink(many=True, read_only=True)
    children = ChildrenSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('url', 'id', 'name', 'description', 'image_url', 'children', 'parents')
