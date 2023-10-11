from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from buyandsell.models import Product
from upload.models import UploadedImage
from events.models import Event
from bodies.models import Body
from venter.models import ComplaintImage
from community.models import Community, CommunityPost


class Command(BaseCommand):
    help = "Check claims and clean unclaimed images."

    def handle(self, *args, **options):
        """Check claims and clean unclaimed images."""

        # Look for claims for unclaimed images
        cleaned = 0
        for image in UploadedImage.objects.filter(is_claimed=False):
            # Check if the image was uploaded in the last hour
            if (timezone.now() - image.time_of_creation).total_seconds() < 3600:
                continue

            # Initialize
            url = image.picture.url
            claimant = None

            # Get a list of possible claimants
            queries = [
                Event.objects.filter(image_url__contains=url),
                Body.objects.filter(image_url__contains=url),
                ComplaintImage.objects.filter(image_url__contains=url),
                Community.objects.filter(
                    Q(logo_image__contains=url) | Q(cover_image__contains=url)
                ),
                CommunityPost.objects.filter(image_url__contains=url),
                Product.objects.filter(product_image__contains=url),
            ]

            # Look for claimants
            for query in queries:
                if query.exists():
                    claimant = query.first()
                    break

            # Save the claimant if found, otherwise cleanup
            if claimant:
                print(image.picture.url, "claimed by", claimant)
                image.claimant = claimant
                image.is_claimed = True
                image.save()
            else:
                print(
                    "No claimant found for",
                    image.picture.url,
                    "(%s)" % str(image.uploaded_by),
                )
                image.delete()
                cleaned += 1

        # Validate claims on claimed images
        verified = 0
        for image in UploadedImage.objects.prefetch_related("claimant").filter(
            is_claimed=True
        ):
            if (
                not image.claimant  # pylint: disable=R0916
                or (
                    not isinstance(image.claimant, Community)
                    and image.picture.url not in image.claimant.image_url
                )
                or (
                    isinstance(image.claimant, Community)
                    and image.picture.url not in image.claimant.logo_image
                    and image.picture.url not in image.claimant.cover_image
                )
            ):
                print(
                    "Invalid claimant for",
                    image.picture.url,
                    "(%s)" % str(image.uploaded_by),
                )
                image.delete()
                cleaned += 1
            else:
                verified += 1

        self.stdout.write(
            self.style.SUCCESS(
                "%i uploaded image claims verified, %i cleaned" % (verified, cleaned)
            )
        )
