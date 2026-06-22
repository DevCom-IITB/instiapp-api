import re
import html
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from slugify import slugify

from .models import CompanyThread, BlogPost, ExtractedData
from .nlp_helpers import infer_domain

from .data_extractor import (
    extract_fields,
    extract_interview_slots,
    extract_roll_numbers,
    normalize_company_name,
    company_slug,
    extract_post_type
)

@receiver(post_save, sender=BlogPost)
def auto_sync_and_extract_post(sender, instance, created, **kwargs):
    if not instance.thread:
        comp_name = normalize_company_name(instance.raw_company_name)
        c_slug = company_slug(instance.raw_company_name)
        
        company_thread, _ = CompanyThread.objects.get_or_create(
            company_name=comp_name,
            defaults={
                'company_slug': c_slug,
                'first_post_date': instance.published
            }
        )
        # Link the post back to the thread using update() to avoid recursion loops
        BlogPost.objects.filter(id=instance.id).update(thread=company_thread)
        instance.thread = company_thread

    # Get the parent thread instance for roll-up operations
    thread = instance.thread

    # Fetch or initialize the corresponding 1-to-1 ExtractedData record
    ext_data, _ = ExtractedData.objects.get_or_create(post=instance)

    # Dynamic Field Processing based on Post Type
    if instance.post_type == 'IAF_OPEN':
        # Use your custom text extraction engine
        data = extract_fields(instance.raw_content)
        
        # Parse the custom profiles list into the multi-domain spaCy system
        raw_roles_list = data.get('raw_roles_list', [])
        unique_domains = set()
        for individual_role in raw_roles_list:
            domain = infer_domain(individual_role.lower())
            if domain and domain != '[UNMATCHED]':
                unique_domains.add(domain)

        final_domain_string = ', '.join(sorted(unique_domains)) if unique_domains else 'General'

        # Sync down to specific ExtractedData entry
        ext_data.category = data.get('category', '')
        ext_data.role = data.get('role', '')
        ext_data.domain = final_domain_string
        ext_data.stipend = data.get('stipend', '')
        ext_data.eligibility = data.get('eligibility', '')
        ext_data.deadline = data.get('deadline')
        ext_data.event_date = data.get('event_date')
        ext_data.venue = data.get('venue', '')
        ext_data.reporting_time = data.get('reporting_time', '')
        ext_data.save()

        # Roll up master data to update the overarching parent CompanyThread
        thread.category = ext_data.category
        thread.role = ext_data.role
        thread.domain = ext_data.domain
        thread.stipend = ext_data.stipend
        thread.eligibility = ext_data.eligibility
        thread.iaf_deadline = ext_data.deadline
        thread.save()

    elif instance.post_type in ['INTERVIEW_SCHEDULE', 'GD_SCHEDULE']:
        ext_data.interview_slots = extract_interview_slots(instance.raw_content)
        ext_data.save()

    elif 'SHORTLIST' in instance.post_type:
        ext_data.shortlisted_rolls = extract_roll_numbers(instance.raw_content)
        ext_data.save()