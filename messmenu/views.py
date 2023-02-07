"""Views for mess menu."""
from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from cryptography.fernet import Fernet
from messmenu.models import Hostel, MessCalEvent
from messmenu.serializers import HostelSerializer, MessCalEventSerializer
from django.utils.timezone import make_aware

@api_view(['GET', ])
def get_mess(request):
    """Get mess menus of all hostels."""
    queryset = Hostel.objects.all()
    queryset = HostelSerializer.setup_eager_loading(queryset)
    return Response(HostelSerializer(queryset, many=True).data)

@api_view(['GET', ])
def getUserMess(request):
    """Get mess status for a user"""

    try:
        request.user.profile
    except AttributeError:
        return Response({
            'message': 'unauthenticated',
            'detail': 'Log in to continue!'
        }, status=401)

    user = request.user.profile
    rollno = user.roll_no

    start = request.GET.get('start')
    end = request.GET.get('end')

    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

    curr = start

    items = []

    while curr <= end:
        url = f'{settings.MESSI_BASE_URL}/api/get_details?roll={rollno}&year={curr.year}&month={curr.month}'
        payload = {}
        headers = {
            'x-access-token': settings.MESSI_ACCESS_TOKEN
        }

        res = requests.request("GET", url, headers=headers, data=payload)

        if res.status_code != 200:
            curr = curr + relativedelta(months=1)
            continue
            # print("Error in getting details")
            # return Response({"error":"Error in getting mess calendar"})

        data = res.json()

        try:
            details = data["details"]

            for d in details:
                k = binaryDecode(d)
                mealnum = k["meal"]

                mealnumtotitle = {
                    "000": "Breakfast",
                    "001": "Lunch",
                    "010": "Snacks",
                    "011": "Dinner",
                    "100": "Milk",
                    "101": "Egg",
                    "110": "Fruit"
                }

                if mealnum in mealnumtotitle:
                    title = mealnumtotitle[mealnum]
                else:
                    title = "Other"

                date = datetime(curr.year, curr.month, k["day"], k["time"] // 60, k["time"] % 60)
                date = make_aware(date)
                hostel = k["hostel"]

                item, c = MessCalEvent.objects.get_or_create(user=user, datetime=date, hostel=hostel)
                if c or item.title != title:
                    item.title = title
                    item.save()

                items.append(item)

        except KeyError:
            curr = curr + relativedelta(months=1)
            continue

        curr = curr + relativedelta(months=1)

    return Response(MessCalEventSerializer(items, many=True).data)


def binaryDecode(x):
    b_x = "{0:b}".format(int(x))
    day = int(b_x[len(b_x) - 5:len(b_x)], 2)
    meal = b_x[len(b_x) - 8:len(b_x) - 5]
    time = int(b_x[len(b_x) - 19:len(b_x) - 8], 2)
    hostel = int(b_x[0:len(b_x) - 19], 2)
    return {'hostel': hostel, 'time': time, 'meal': meal, 'day': day}

@api_view(['GET', ])
def getRnoQR(request):

    try:
        request.user.profile
    except AttributeError:
        return Response({
            'message': 'unauthenticated',
            'detail': 'Log in to continue!'
        }, status=401)

    try:
        user = request.user.profile
        rollno = (str(user.roll_no)).upper()
        # rollno = "200020087"
        time = str(datetime.now())
        rnom = (rollno + "," + time).encode()

        f = Fernet(b'Tolm_fRDkfoN5WMU4oUXWxNwmn1E0MmYlbeh1LA29cU=')
        encrRno = f.encrypt(rnom)

        return Response({"qrstring": encrRno})
    except Exception as e:
        return Response({
            'qrstring': str(e),
        })
