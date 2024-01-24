"""Views for BuyAndSell."""
import json
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from roles.helpers import login_required_ajax
from buyandsell.models import Ban, Category, ImageURL, Limit, Product, Report
from buyandsell.serializers import ProductSerializer
from helpers.misc import query_search
from users.models import UserProfile

REPORTS_THRES = 3


class BuyAndSellViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    RESULTS_PER_PAGE = 1  # testing purposes.
    queryset = Product.objects

    def mail_moderator(self, report: Report):
        msg = f"""
        {str(report.reporter)} lodged a report against the product
        {str(report.product)} posted by {str(report.product.user)}.
        Alleged Reason: {report.reason}."""
        send_mail(
            "New Report", msg, settings.DEFAULT_FROM_EMAIL, [report.moderator_email]
        )

    def update_limits(self):
        for limit in Limit.objects.all():
            if limit.endtime is not None and limit.endtime < timezone.localtime():
                limit.delete()

    def update_bans(self, product: Product = None):
        if product is not None:
            """Get the existing reports on this product that have been accepted by the moderator
            but have not been addressed (by initiating a ban)."""
            reports = Report.objects.filter(
                product=product, addressed=False, accepted=True
            )
            if len(reports) >= REPORTS_THRES:
                """Create a ban for the user lasting three days."""
                endtime = timezone.localtime() + timezone.timedelta(days=3)
                Ban.objects.create(user=product.user, endtime=endtime)
                product.deleted = True
                reports.update(addressed=True)
        else:
            """Calls the above if-block on products that have accepted but unaddressed reports."""
            reports = Report.objects.filter(accepted=True, addressed=False)
            products = []
            for report in reports:
                products.append(report.product)
            for prod in set(products):
                if products.count(prod) >= REPORTS_THRES:
                    """Products from a banned user cannot be reported. (acc. to report function.)"""
                    endtime = timezone.localtime() + timezone.timedelta(days=3)
                    Ban.objects.create(user=product.user, endtime=endtime)
                    reports.update(addressed=True)

    def category_filter(self, request, queryset):
        category = request.GET.get("category")
        if category is not None and len(Category.objects.filter(name=category)) > 0:
            queryset = queryset.filter(category__name=category)
        return queryset

    def seller_filter(self, request, queryset):
        seller = request.GET.get("seller")
        if seller is not None and len(UserProfile.objects.filter(ldap_id=seller)) > 0:
            queryset = queryset.filter(user=UserProfile.objects.get(ldap_id=seller))
        return queryset

    def list(self, request):
        # introduce tags?
        self.update_bans()
        queryset = self.queryset.filter(status=True)
        """remove products from banned users"""
        bans = Ban.objects.all()
        for ban in bans:
            if ban.endtime > timezone.localtime():
                """Remove products from users whose bans are still running."""
                queryset = queryset.filter(~Q(user=ban.user))
        # TODO: allow category to be passed here too.
        queryset = query_search(
            request, 3, queryset, ["name", "description"], "buyandsell"
        )
        queryset = self.category_filter(request, queryset)
        queryset = self.seller_filter(request, queryset)
        # queryset = query_from_num(request, self.RESULTS_PER_PAGE, queryset)
        data = ProductSerializer(queryset, many=True).data
        return Response(data)

    def get_contact_details(self, userpro: UserProfile):
        return f"""
 Phone: {userpro.contact_no}
 Email: {userpro.email}"""

    def update_image_urls(self, request, instance, image_urls=[]):
        if len(image_urls) == 0:
            image_urls = json.loads(request.data["image_urls"])
        ImageURL.objects.filter(product=instance).delete()
        for url in image_urls:
            ImageURL.objects.create(product=instance, url=url)

    def update_user_details(self, request):
        request.data["user"] = UserProfile.objects.get(user=request.user).id
        request.data["contact_details"] = BuyAndSellViewSet.get_contact_details(
            UserProfile.objects.get(user=request.user)
        )
        return request

    @login_required_ajax
    def create(self, request):
        """Creates product if the user isn't banned and form is filled
        correctly. Ban checking is yet to be incorporated.
        """

        self.update_limits()
        from users.models import UserProfile

        userpro = UserProfile.objects.get(user=request.user)

        """Limit checking:"""
        limit, created = Limit.objects.get_or_create(user=userpro)
        if limit.strikes >= 1000:
            return Response("Limit of Three Products per Day Reached.", status=403)
        limit.strikes += 1
        if limit.strikes == 3:
            limit.endtime = timezone.localtime() + timezone.timedelta(days=1)
        limit.save()
        """Create the product, modifying some fields."""
        # request.data._mutable = True
        # request.data['status'] = True
        # image_urls = json.loads(request.data['image_urls'])
        # request.data['contact_details'] = BuyAndSellViewSet.get_contact_details(userpro)
        # request.data['user'] = userpro.id
        # print(request.data)

        try:
            return super().create(request)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @login_required_ajax
    def destroy(self, request, pk):
        product = self.get_product(pk)
        if UserProfile.objects.get(user=request.user) == product.user:
            return super().destroy(request, pk)  # maybe change return arg?
        return Response(ProductSerializer(product).data)

    def get_product(self, pk):
        return get_object_or_404(self.queryset, id=pk)

    @login_required_ajax
    def update(self, request, pk):
        product = self.get_product(pk)
        # TO TEST:
        # product.category.numproducts-=1
        # product.category.numproducts-=1
        if product.user == UserProfile.objects.get(user=request.user):
            #    request.data._mutable = True
            #    request.data._mutable = True
            request = self.update_user_details(request)
            #    self.update_image_urls(request, product)
            return super().update(request, pk)
        return Response(ProductSerializer(product).data)

    def retrieve(self, request, pk):
        product = self.get_product(pk)
        return Response(ProductSerializer(product).data)

    @login_required_ajax
    def report(self, request, pk):
        product = self.get_product(pk)
        self.update_bans(product)
        if len(Ban.objects.filter(user=product.user)) > 0:
            """If user is banned, their products don't show up in the list.
            This if-block is for calls made to the api manually."""
            return Response("User is Banned atm.")
        reporter = UserProfile.objects.get(user=request.user)
        # reporter = product.user
        report_by_user, created = Report.objects.get_or_create(
            product=product, reporter=reporter
        )
        report_by_user: Report
        report_by_user.reason = request.data["reason"]
        report_by_user.save()
        self.mail_moderator(report_by_user)
        return Response(ProductSerializer(product).data)

    def get_categories(self, request):
        return Response(
            json.dumps({x.name: x.numproducts for x in Category.objects.all()})
        )
