' Serializers for Body and BodyChildRelation '
from rest_framework import serializers
from rest_framework.reverse import reverse
from bodies.models import Body

class ParentBodyHyperlink(serializers.HyperlinkedRelatedField):
    ' Gets hyperlinks for parent bodies from BodyChildRelation'
    view_name = 'body-detail'

    def get_url(self, obj, view_name, request, format): # pylint: disable=redefined-builtin
        url_kwargs = {'pk': obj.parent.pk}
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

class ChildrenSerializer(serializers.ModelSerializer):
    ' Serializes children of the body from BodyChildRelation'
    def to_representation(self, instance):
        return BodySerializer(instance.child, context=self.context).data

class BodySerializerMin(serializers.HyperlinkedModelSerializer):
    ' Minimal serializer for Body '

    class Meta:
        model = Body
        fields = ('url', 'id', 'name', 'description', 'image_url')

class BodyFollowersSerializer(serializers.HyperlinkedModelSerializer):
    ' Minimal serializer for Body '

    from users.serializers import UserProfileSerializer

    followers = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('url', 'id', 'followers')

class BodySerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Body'

    from events.serializers import EventSerializer

    followers_url = serializers.HyperlinkedIdentityField(view_name='body-followers')
    followers_count = serializers.SerializerMethodField()

    parents = ParentBodyHyperlink(many=True, read_only=True)
    children = ChildrenSerializer(many=True, read_only=True)

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('url', 'id', 'name', 'description', 'image_url', 
                  'children', 'parents', 'events', 'followers_url',
                  'followers_count')

    def get_followers_count(self, obj):
        return obj.followers.all().count()
