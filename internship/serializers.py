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

class CompanyThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyThread
        fields = [
            'id', 'company_name', 'company_slug', 'first_post_date',
            'category', 'role', 'domain', 'stipend', 'eligibility', 'iaf_deadline'
        ]

class CompleteThreadSerializer(serializers.ModelSerializer):
    # 'posts' matches the related_name='posts' you defined in the BlogPost model
    posts = BlogPostSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyThread
        fields = [
            'id', 'company_name', 'company_slug', 'first_post_date',
            'category', 'role', 'domain', 'stipend', 'eligibility', 'iaf_deadline',
            'posts'  # This injects the chronological history into the response
        ]