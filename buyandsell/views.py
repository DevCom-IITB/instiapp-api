"""Views for BuyAndSell."""
from datetime import tzinfo
from uuid import UUID
from django.db.models.query import QuerySet
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from roles.helpers import login_required_ajax
from buyandsell.models import Ban, ImageURL, Product, Report
from buyandsell.serializers import ProductSerializer
from helpers.misc import query_from_num, query_search
from users.models import UserProfile
from django.db.models import Count,Q
import json
from django.utils import timezone
REPORTS_THRES = 3

class BuyAndSellViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    RESULTS_PER_PAGE = 1#testing purposes.
    queryset = Product.objects
    def update_bans(self, product=None):
        if(product!=None):
            """Get the existing reports on this product that have been accepted by the moderator
            but have not been addressed (by initiating a ban)."""
            reports = Report.objects.filter(product=product, addressed=False, accepted=True)
            if(len(reports)>=REPORTS_THRES):
                """Create a ban for the user lasting three days."""
                endtime = timezone.localtime()+timezone.timedelta(days=3)
                Ban.objects.create(user=product.user, endtime=endtime)
                reports.update(addressed=True)
        else:
            """Calls the above if-block on products that have accepted but unaddressed reports."""
            reports = Report.objects.filter(accepted=True, addressed=False)
            products = []
            for report in reports:
                products.append(report.product)
            for prod in set(products):
                if(products.count(prod)>=REPORTS_THRES):
                    """Products from a banned user cannot be reported. (acc. to report function.)"""
                    endtime = timezone.localtime()+timezone.timedelta(days=3)
                    Ban.objects.create(user=product.user, endtime=endtime)
                    reports.update(addressed=True)
        """Delete expired bans."""
        bans = Ban.objects.all()
        #check: Ban.objects.filter(endtime__lte=timezone.localtime())
        for ban in bans:
            ban:Ban
            if(ban.endtime<timezone.localtime()):
                ban.delete()
    def list(self, request):
        ##introduce tags?
        self.update_bans()
        queryset = self.queryset.filter(status=True)
        """remove products from banned users"""
        bans = Ban.objects.all()
        for ban in bans:
            queryset = queryset.filter(~Q(user=ban.user))
        queryset = query_search(request, 3, queryset, ['name', 'description'], 'buyandsell')
        queryset = query_from_num(request, self.RESULTS_PER_PAGE, queryset)
        data = ProductSerializer(queryset, many=True).data
        return Response(data)
    def get_contact_details(userpro:UserProfile):
        return f"""
 Phone: {userpro.contact_no}
 Email: {userpro.email}"""
    def update_image_urls(self, request, instance, image_urls=[]):
        if(len(image_urls)==0):
            image_urls = json.loads(request.data['image_urls'])
        ImageURL.objects.filter(product=instance).delete()
        for url in image_urls:
            ImageURL.objects.create(product=instance, url=url)  
    def update_user_details(self, request):
        request.data['user'] = UserProfile.objects.get(user=request.user).id
        request.data['contact_details'] = BuyAndSellViewSet.get_contact_details(UserProfile.objects.get(user=request.user))
        return request  
    @login_required_ajax
    def create(self, request):
        """Creates product if the user isn't banned and form is filled
        correctly. Ban checking is yet to be incorporated.
        """
        from users.models import UserProfile
        userpro = UserProfile.objects.get(user=request.user)
        userpro:UserProfile
        request.data._mutable = True
        request.data['status'] = True
        image_urls = json.loads(request.data['image_urls'])
        request.data['contact_details'] = BuyAndSellViewSet.get_contact_details(userpro)
        request.data['user'] = userpro.id
        
        new_product_data = super().create(request)
        instance = Product.objects.get(new_product_data.data['id'])
        self.update_image_urls(request, instance)
        return Response(ProductSerializer(instance).data)
    @login_required_ajax
    def destroy(self, request, pk):
        product = self.get_product(pk)
        if(UserProfile.objects.get(user=request.user)==product.user):
            return super().destroy(request, pk) #maybe change return arg?
        return Response(ProductSerializer(product).data)
    def get_product(self, pk):
        return get_object_or_404(self.queryset, id=pk)

    @login_required_ajax
    def update(self, request, pk):
        product = self.get_product(pk)
        if(product.user == UserProfile.objects.get(user=request.user)):
            request.data._mutable = True
            request = self.update_user_details(request)
            self.update_image_urls(request, product)
            return super().update(request, pk)
        return Response(ProductSerializer(product).data)

    def retrieve(self, request, pk):
        product = self.get_product(pk)
        return Response(ProductSerializer(product).data)
    
    @login_required_ajax
    def report(self, request, pk):
        product = self.get_product(pk)

        if(len(Ban.objects.filter(user=product.user))>0):
            """If user is banned, their products don't show up in the list. 
            This if-block is for calls made to the api manually."""
            return Response('User is Banned atm.')


        reporter = UserProfile.objects.get(user=request.user)
        report_by_user,created = Report.objects.get_or_create(product=product, reporter=reporter)
        report_by_user:Report
        report_by_user.reason = request.data['reason']
        report_by_user.save()
        """SEND EMAIL TO MODERATOR"""
        self.update_bans(product)
        return Response(ProductSerializer(product).data)