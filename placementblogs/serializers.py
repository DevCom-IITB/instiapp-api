from rest_framework import serializers
from .models import PlacementCompanyThread, PlacementBlogPost, PlacementExtractedData

class PlacementExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementExtractedData
        exclude = ['post', 'id'] 

class PlacementBlogPostSerializer(serializers.ModelSerializer):
    extracted_data = PlacementExtractedDataSerializer(source='extracted', read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    company_slug = serializers.ReadOnlyField(source='thread.company_slug')

    class Meta:
        model = PlacementBlogPost
        fields = [
            'id', 'company_slug', 'post_type', 'post_type_display', 'raw_company_name', 
            'published', 'link', 'pinned', 'extracted_data', 'raw_content'
        ]

class PlacementCompanyThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementCompanyThread
        fields = [
            'id', 'company_name', 'company_slug', 'first_post_date',
            'role', 'domain', 
            'bonus_jaf', 'cpi_cutoff', 'bond', 'mode', 'jaf_deadline' 
        ]

class PlacementCompleteThreadSerializer(serializers.ModelSerializer):
    posts = PlacementBlogPostSerializer(many=True, read_only=True)

    class Meta:
        model = PlacementCompanyThread
        fields = [
            'id', 'company_name', 'company_slug', 'first_post_date',
            'role', 'domain', 
            'bonus_jaf', 'cpi_cutoff', 'bond', 'mode', 'jaf_deadline',
            'posts' 
        ]