from rest_framework import serializers
from .models import CompanyThread, BlogPost, ExtractedData

class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        exclude = ['post', 'id']

class BlogPostSerializer(serializers.ModelSerializer):
    extracted_data = ExtractedDataSerializer(source='extracted', read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'post_type', 'post_type_display', 'raw_company_name', 
            'published', 'link', 'pinned', 'extracted_data'
        ]

# Sample output
# {
#     "id": "5d1f7a3c-1234-5678",
#     "post_type": "IAF_OPEN",
#     "post_type_display": "IAF Open",
#     "raw_company_name": "Google",
#     "published": "2025-06-01T10:00:00Z",
#     "link": "https://example.com/post",
#     "pinned": false,
#     "extracted_data": {
#         "category": "I1",
#         "role": "Software Engineer",
#         "domain": "Backend",
#         "stipend": "50000",
#         "eligibility": "B.Tech CSE"
#     }
# }

class CompanyThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyThread
        fields = [
            'id', 'company_name', 'company_slug', 'first_post_date',
            'category', 'role', 'domain', 'stipend', 'eligibility', 'iaf_deadline'
        ]