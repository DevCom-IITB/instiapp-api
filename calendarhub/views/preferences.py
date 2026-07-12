# calendarhub/views/preferences.py
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from calendarhub.models import CalendarSourcePreference, CalendarBodyPreference
from calendarhub.serializers import CalendarSourcePreferenceSerializer



PREFS_TTL = 3600  # 1 hour


def _prefs_key(user_id):
    return f'calendar:user:{user_id}:preferences'


class CalendarPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.profile

        

       
        prefs, _ = CalendarSourcePreference.objects.get_or_create(user=user)
        serializer = CalendarSourcePreferenceSerializer(prefs)

       
        return Response(serializer.data)

    def patch(self, request):
        user = request.user.profile
        prefs, _ = CalendarSourcePreference.objects.get_or_create(user=user)
        serializer = CalendarSourcePreferenceSerializer(prefs, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
           
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CalendarBodyPreferenceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user.profile
        followed_bodies = user.followed_bodies.all()
        body_prefs = {
            str(bp.body_id): bp.enabled
            for bp in CalendarBodyPreference.objects.filter(user=user)
        }
        result = [
            {
                'body_id':   str(body.id),
                'body_name': body.name,
                'enabled':   body_prefs.get(str(body.id), True),
            }
            for body in followed_bodies
        ]
        return Response(result)


class CalendarBodyPreferenceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, body_id):
        enabled = request.data.get('enabled')
        if enabled is None:
            return Response(
                {'error': 'enabled field is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user.profile
        if not user.followed_bodies.filter(id=body_id).exists():
            return Response(
                {'error': 'You do not follow this body'},
                status=status.HTTP_404_NOT_FOUND,
            )
        CalendarBodyPreference.objects.update_or_create(
            user=user,
            body_id=body_id,
            defaults={'enabled': enabled},
        )
       

        return Response({'body_id': str(body_id), 'enabled': enabled})
