# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from calendarhub.models import ExternalCalendarAccount
# from calendarhub.serializers import ExternalCalendarAccountSerializer


# class ResobinsyncronizerView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         from calendarhub.tasks.resobin_sync import sync_resobin_for_user
#         user = request.user.profile
#         sync_resobin_for_user.delay(str(user.id))
#         return Response({'enqueued': True})

#     def get(self, request):
#         user = request.user.profile
#         try:
#             account = ExternalCalendarAccount.objects.get(user=user, provider='resobin')
#             return Response(ExternalCalendarAccountSerializer(account).data)
#         except ExternalCalendarAccount.DoesNotExist:
#             return Response({'status': 'not_synced', 'last_sync_at': None})
