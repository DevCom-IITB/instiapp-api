' Serializers for Body and BodyChildRelation '
from rest_framework import serializers
from bodies.models import Body

class ChildrenSerializer(serializers.ModelSerializer):
    ' Serializes children of the body from BodyChildRelation'
    def to_representation(self, instance):
        return BodySerializer(instance.child, context=self.context).data

class BodySerializerMin(serializers.ModelSerializer):
    ' Minimal serializer for Body '

    class Meta:
        model = Body
        fields = ('id', 'name', 'description', 'image_url')

class BodyFollowersSerializer(serializers.ModelSerializer):
    ' Minimal serializer for Body '

    from users.serializers import UserProfileSerializer

    followers = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('id', 'followers')

class BodySerializer(serializers.ModelSerializer):
    'Serializer for Body'

    from events.serializers import EventSerializer

    followers_count = serializers.SerializerMethodField()

    parents = serializers.SerializerMethodField()
    children = ChildrenSerializer(many=True, read_only=True)

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('id', 'name', 'description', 'image_url',
                  'children', 'parents', 'events', 'followers_count')

    def get_followers_count(self, obj):
        return obj.followers.all().count()

    def get_parents(self, obj):
        return [x.parent.id for x in obj.parents.all()]
